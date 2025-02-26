async function compute_amount_form2(input) {
  const entry = new Decimal(document.getElementById('form2_entry').value || 0)
    const stop = new Decimal(document.getElementById('form2_stop').value || 0)
    const target = new Decimal(document.getElementById('form2_target').value || 0)
    const amountel = new Decimal(document.getElementById('form2_amount').value || 0)
    const symbol = document.getElementById('form2_symbol').value
    const broker = document.getElementById('form2_broker').value
    const stop_percent = entry.minus(stop).dividedBy(entry).times(new Decimal(100))
    console.log(entry.toFixed(4), stop.toFixed(4), target.toFixed(4), amountel.toFixed(4), symbol, broker, stop_percent.toFixed(4))
    const risk = await get_risk(broker, symbol)
    const rr = target.minus(entry).dividedBy(entry.minus(stop)).toFixed(4)
    const commission = await get_commission(symbol, broker)
    document.getElementById('form2_commission').value = commission
    let amount = new Decimal(risk).dividedBy((stop_percent.plus(commission).dividedBy(new Decimal(100))))
    document.getElementById('form2_amount').value = amount.toFixed(4) 
    console.log('risk is: ', risk, "type of risk is :", typeof (risk), ' and commission is: ', commission)
    console.log(amount.toFixed(4), stop_percent.toFixed(4))
}
$("#form2 input").keyup(compute_amount_form2)
