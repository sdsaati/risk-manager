function compute_amount_form2(input) {
  const broker = document.getElementById('broker')
  if (broker.value != "" && input != null){
    handleSelectChange(broker)
  }
 
  /*
   * UB IS:
  "balance": ub.balance,
  "defined_reserve": ub.defined_reserve,
  "risk_percent": ub.riskPercent,
  "reserve_percent": ub.reservePercent,
  "current_reserve": ub.reserve,
  "available": ub.available_balance,
  "risk": ub.risk,
  "commission": commission,
  */
 
  // (((ub.balance - ub.available) * ub.risk_percent)/ub.available) + ub.risk_percent
  const risk_percent = new Decimal(ub.balance).minus(ub.available).times(ub.risk_percent).dividedBy(ub.available).plus(ub.risk_percent)
  const risk = new Decimal(risk_percent).times(ub.available).dividedBy(100)
  const commission = ub.commission

  const entry = new Decimal(document.getElementById('form2_entry').value || 0)
  const stop = new Decimal(document.getElementById('form2_stop').value || 0)
  const target = new Decimal(document.getElementById('form2_target').value || 0)
  const amountel = new Decimal(document.getElementById('form2_amount').value || 0)


  /* NOTE: User must not enter a stop that its stoploss% be less than its risk */
  // stop(%)  =  ( (entry - stop) / entry) * 100
  let stop_percent = entry.minus(stop).dividedBy(entry).times(new Decimal(100))
  if (stop_percent.lt(risk_percent)) {
      stop_percent = risk_percent
      document.getElementById('form2_stop').value = entry.times(new Decimal(1).minus(stop_percent.dividedBy(new Decimal(100)))).toFixed(4)
  }



  const rr = target.minus(entry).dividedBy(entry.minus(stop)).toFixed(4)
  let amount = new Decimal(risk).dividedBy((stop_percent.plus(commission).dividedBy(new Decimal(100))))


  document.getElementById('form2_commission').value = commission
  document.getElementById('form2_amount').value = amount.toFixed(4)
  document.getElementById('form2_amount_percent').innerHTML = "<pre>" + amount.dividedBy(ub.balance).times(100).toFixed(0) + "% of account balance("+ ub.balance.toFixed(4) + ")</pre>"


  document.getElementById('loss').innerHTML = "<pre>" + ub.balance.toFixed(4) +  " - " + ub.balance.minus(ub.balance.minus(risk.plus(commission))).toFixed(4) + "</pre>"
  document.getElementById('win').innerHTML = "<pre>" + ub.balance.toFixed(4) + " + " + ub.balance.plus(risk.minus(commission).times(rr)).minus(ub.balance).toFixed(4) + "</pre>"




}
