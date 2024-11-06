import Decimal from "./decimal.mjs"

function compute_amount(input) {
    let entry = document.getElementsByName('entry')
    let stop = document.getElementsByName('stop')
    let amountel = document.getElementsByName('amount')
    let stop_percent = ((entry - stop) / entry) * 100
    let amount = window.risk / ((stop_percent + window.commission) / 100)
    amountel.value = amount
    console.log('risk is: ', window.risk, "type of risk is :", typeof (window.risk), ' and commission is: ', window.commission)
    console.log(amount)
}

/* Running */
$("input").change(compute_amount)
console.log(Decimal('25.5'))