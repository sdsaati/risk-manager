function compute_amount_form1(input) {
  //init_ub()  /* this will set window.ub */
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

  let stop_percent = new Decimal(document.getElementById('form1_stopp').value || risk_percent)
  if (stop_percent < risk_percent) {
    stop_percent = risk_percent
  }
  const rr = new Decimal(document.getElementById('form1_risk_reward').value || 0)
  let server_risk = new Decimal(ub.risk)
  const amountel = new Decimal(document.getElementById('form1_amount').value || 0)


  /* 
   amount = risk / ((( stop_percent + ub.commission )) / 100)
  */
  let amount = new Decimal(risk).dividedBy((stop_percent.plus(ub.commission).dividedBy(new Decimal(100))))

  document.getElementById('form1_commission').value = ub.commission
  document.getElementById('form1_amount').value = amount.toFixed(4) 
}
