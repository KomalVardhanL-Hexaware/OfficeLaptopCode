// testExample.js

function add(a, b) {
    return a + b;
}

function subtract(a, b) {
    return a - b;
}

function multiply(a, b) {
    return a * b;
}

function divide(a, b) {
    if (b === 0) {
        throw new Error("Cannot divide by zero");
    }
    return a / b;
}

const x = 10;
const y = 5;
console.log("Sum:", add(x, y));
console.log("Difference:", subtract(x, y));
console.log("Product:", multiply(x, y));
console.log("Quotient:", divide(x, y));
