from pycli import run_application, add_cli


@add_cli()
def factorial(n:int) -> int:
    '''Calculates factorial of nonnegative integer n.

    Args:
        n: Integer to calculate factorial of.

    Returns:
        n!, the factorial of n.
    '''

    if n < 0:
        print('Factorial argument n must be a natural number.')
        raise ValueError

    ret = 1
    for i in range(2, n + 1):
        ret *= i

    return ret


if __name__ == '__main__':
    run_application()
