public class TestExample {
    public static int add(int a, int b) {
        return a + b;
    }

    public static int subtract(int a, int b) {
        return a - b;
    }

    public static int multiply(int a, int b) {
        return a * b;
    }

    public static int divide(int a, int b) {
        if (b == 0) {
            throw new IllegalArgumentException("Cannot divide by zero");
        }
        return a / b;
    }

    public static void main(String[] args) {
        int x = 10;
        int y = 5;
        System.out.println("Sum: " + add(x, y));
        System.out.println("Difference: " + subtract(x, y));
        System.out.println("Product: " + multiply(x, y));
        System.out.println("Quotient: " + divide(x, y));
    }
}
