#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations  # Delays evaluation of type hints until runtime

import logging
from typing import Any
from abc import ABC, abstractmethod
from decimal import Decimal as d
from decimal import getcontext
from copy import copy, deepcopy
from django.db.models import QuerySet  # for typehint of records
from trade.models import Symbol, Trade, UserBroker

logger = logging.getLogger("django")
getcontext().prec = 4


class TradeStateManager:
    """
    Use this class to decide going to which state depends on the
    state of trade
    *there are some computational fields that we must care about them.*
    """

    def __init__(
        self,
        trade_edited_record: Trade,
        trade_before_edit_record: Trade,
        trade_class: Trade,
    ):
        self.trade_edited_record: Trade = trade_edited_record
        self.trade_before_edit_record: Trade = trade_before_edit_record
        self.trade_class: Trade = trade_class
        self.goto(Decision())  # The first state that decides what we do

    def goto(self, state: State):
        self.state = state
        self.state.state_manager = self
        self.state.log()
        self.state.handle()


class State(ABC):
    _state_manager: TradeStateManager

    def __init__(self):
        getcontext().prec = 4

    @property
    def state_manager(self) -> TradeStateManager:
        return self._state_manager

    @state_manager.setter
    def state_manager(self, sm: TradeStateManager) -> None:
        self._state_manager = sm

    @abstractmethod
    def handle(self) -> None:
        """
        All the states must implement this method
        whenever we go to a state, this is the first entrypoint
        that will be executed.
        """
        raise NotImplementedError("This is an Abstract method\nYou cannot call it.")

    def log(self, msg: Any = None) -> None:
        if msg is not None:
            logger.warn(msg)
        else:
            logger.warn(f">> {str(self)}")
            if self.prev() is not None:
                logger.warn("PrevRecordID=" + str(self.prev().id))
            logger.warn("BeforeEditID=" + str(self.before().id))
            logger.warn("AfterEditID =" + str(self.after().id))

    def get_trade_class(self) -> Trade:
        return self.state_manager.trade_class

    def prev(self) -> Trade | None:
        return (
            self.get_trade_class()
            .objects.filter(id__lt=self.state_manager.trade_edited_record.id)
            .order_by("-id")
            .first()
        )

    def before(self) -> Trade:
        return self.state_manager.trade_before_edit_record

    def after(self) -> Trade:
        return self.state_manager.trade_edited_record

    def all_records_after(self, pk_id=None) -> QuerySet[Trade] | None:
        if pk_id is None:
            pk_id = self.after().id
        try:
            records: QuerySet[Trade] = self.get_trade_class().objects.filter(
                id__gt=pk_id
            )
            for record in records:
                self.log(str(record.id))
            return records
        except Trade.DoesNotExist:
            return None

    def casace_update_trades_after_here(self):
        b = copy(self.after().ub.balance)
        r = copy(self.after().ub.reserve)
        for record in self.all_records_after(self.after().id):
            self.log(f"we are cascading update Trade.id: {record.id}")
            record.update_reserve_and_balance(
                previews_trade_balance=b, previews_trade_reserve=r, save=True
            )
            record.amount = copy(record.amount_per_trade)
            b = copy(record.ub.balance)
            r = copy(record.ub.reserve)


class Decision(State):
    def handle(self):
        if self.state_manager.trade_before_edit_record.result is None:
            if self.state_manager.trade_edited_record.result is None:
                self.state_manager.goto(NoneToNone())
            elif (
                self.state_manager.trade_edited_record.result == True
                or self.state_manager.trade_edited_record.result == False
            ):
                self.state_manager.goto(NoneToTrueOrFalse())
        elif self.state_manager.trade_before_edit_record.result == True:
            if self.state_manager.trade_edited_record.result is None:
                self.state_manager.goto(NoneToNone())
            elif self.state_manager.trade_edited_record.result == True:
                self.state_manager.goto(TrueToFalseViceVerca())
            elif self.state_manager.trade_edited_record.result == False:
                self.state_manager.goto(TrueToFalseViceVerca())
        elif self.state_manager.trade_before_edit_record.result == False:
            if self.state_manager.trade_edited_record.result is None:
                self.state_manager.goto(NoneToNone())
            elif self.state_manager.trade_edited_record.result == True:
                self.state_manager.goto(TrueToFalseViceVerca())
            elif self.state_manager.trade_edited_record.result == False:
                self.state_manager.goto(TrueToFalseViceVerca())


class NoneToNone(State):
    """
    balance should be the previews row balance
    reserve should be the previews row reserve
    amount must computed again
    """

    def handle(self):
        try:
            self.after().ub.balance = self.prev().ub.balance
            self.after().ub.reserve = self.prev().ub.reserve
        except:
            self.after().ub.balance = UserBroker.objects.first().balance
            self.after().ub.reserve = UserBroker.objects.first().reserve
        self.after().amount = self.after().amount_per_trade
        # alls = self.all_records_after()


class NoneToTrueOrFalse(State):
    """
    balance must be computed with new result
    reserve must be computed with new result
    amount maybe need to be corrected so we computed it again
    """

    def handle(self):
        self.after().update_reserve_and_balance(
            previews_trade_balance=self.before().ub.balance,
            previews_trade_reserve=self.before().ub.reserve,
        )
        self.after().amount = self.after().amount_per_trade
        self.casace_update_trades_after_here()


class TrueToFalseViceVerca(State):
    """
    balance must be updated from the previews record
    reserve must be updated from the previews record
    amount must compute again
    """

    def handle(self):
        try:
            self.after().update_reserve_and_balance(
                previews_trade_balance=self.prev().ub.balance,
                previews_trade_reserve=self.prev().ub.reserve,
            )
        except:
            self.after().update_reserve_and_balance(
                previews_trade_balance=UserBroker.objects.first().balance,
                previews_trade_reserve=UserBroker.objects.first().reserve,
            )
        self.after().amount = self.after().amount_per_trade
        self.casace_update_trades_after_here()
