#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations  # Delays evaluation of type hints until runtime

import logging
from abc import ABC, abstractmethod
from decimal import Decimal as d
from decimal import getcontext

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

    def log(self):
        logger.warn(f">> {str(self)}")
        logger.warn("PrevRecordID=" + str(self.prev().id))
        logger.warn("BeforeEditID=" + str(self.before().id))
        logger.warn("AfterEditID =" + str(self.after().id))

    def prev(self) -> Trade:
        return (
            self.state_manager.trade_class.objects.filter(
                id__lt=self.state_manager.trade_edited_record.id
            )
            .order_by("-id")
            .first()
        )

    def before(self) -> Trade:
        return self.state_manager.trade_before_edit_record

    def after(self) -> Trade:
        return self.state_manager.trade_edited_record


class Decision(State):
    def handle(self):
        if self.state_manager.trade_before_edit_record.result is None:
            if self.state_manager.trade_edited_record.result is None:
                self.state_manager.goto(NoneToNone())
            elif self.state_manager.trade_edited_record.result == True:
                self.state_manager.goto(NoneToTrue())
            elif self.state_manager.trade_edited_record.result == False:
                self.state_manager.goto(NoneToFalse())
        elif self.state_manager.trade_before_edit_record.result == True:
            if self.state_manager.trade_edited_record.result is None:
                self.state_manager.goto(TrueToNone())
            elif self.state_manager.trade_edited_record.result == True:
                self.state_manager.goto(TrueToTrue())
            elif self.state_manager.trade_edited_record.result == False:
                self.state_manager.goto(TrueToFalse())
        elif self.state_manager.trade_before_edit_record.result == False:
            if self.state_manager.trade_edited_record.result is None:
                self.state_manager.goto(FalseToNone())
            elif self.state_manager.trade_edited_record.result == True:
                self.state_manager.goto(FalseToTrue())
            elif self.state_manager.trade_edited_record.result == False:
                self.state_manager.goto(FalseToFalse())


class NoneToNone(State):
    """
    reserve should be the previews row reserve
    balance should be the previews row balance
    amount must computed again
    """

    def handle(self):
        self.after().ub.reserve = self.prev().ub.reserve
        self.after().ub.balance = self.prev().ub.balance
        self.after().amount = self.after().amount_per_trade
