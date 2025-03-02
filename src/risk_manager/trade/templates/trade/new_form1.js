function compute_amount_form1(input) {
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

  let stop_percent = new Decimal(document.getElementById('form1_stopp').value || risk_percent)
  if (stop_percent.lt(risk_percent)) {
    stop_percent = risk_percent
    document.getElementById('form1_stopp').value = stop_percent.toFixed(4)
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
  document.getElementById('form1_amount_percent').innerHTML = "<pre>" + amount.dividedBy(ub.balance).times(100).toFixed(0) + "% of account balance("+ ub.balance.toFixed(4) + ")</pre>"


  document.getElementById('loss').innerHTML = "<pre>" + ub.balance.minus(risk).toFixed(4) + "</pre>"
  document.getElementById('win').innerHTML = "<pre>" + ub.balance.plus(risk.times(rr)).toFixed(4) + "</pre>"

}
