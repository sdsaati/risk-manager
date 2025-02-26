async function compute_amount_form1(input) {
    const symbol = document.getElementById('form1_symbol').value
    const stop_percent = new Decimal(document.getElementById('form1_stopp').value || 0)
    const rr = new Decimal(document.getElementById('form1_risk_reward').value || 0)
    const broker = document.getElementById('form1_broker').value
    const risk = await get_risk(broker, symbol)
    const amountel = new Decimal(document.getElementById('form1_amount').value || 0)
    const commission = await get_commission(symbol, broker)
    document.getElementById('form1_commission').value = commission
    let amount = new Decimal(risk).dividedBy((stop_percent.plus(commission).dividedBy(new Decimal(100))))
    document.getElementById('form1_amount').value = amount.toFixed(4) 
    console.log('risk is: ', risk, "type of risk is :", typeof (risk), ' and commission is: ', commission)
    console.log(amount.toFixed(4), stop_percent.toFixed(4))
}
$("#form1 input").keyup(compute_amount_form1)
