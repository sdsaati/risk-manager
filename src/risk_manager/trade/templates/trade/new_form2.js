function compute_amount_form2(input) {
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
  const stop_percent = entry.minus(stop).dividedBy(entry).times(new Decimal(100))
  const rr = target.minus(entry).dividedBy(entry.minus(stop)).toFixed(4)
  let amount = new Decimal(risk).dividedBy((stop_percent.plus(commission).dividedBy(new Decimal(100))))


  document.getElementById('form2_commission').value = commission
  document.getElementById('form2_amount').value = amount.toFixed(4)
}
