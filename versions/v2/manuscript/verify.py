import argparse
import hashlib
import json
from math import comb
from pathlib import Path


def multiply(left, right, length):
    output = [0] * length
    for left_index, left_value in enumerate(left[:length]):
        if not left_value:
            continue
        for right_index in range(min(len(right), length - left_index)):
            if right[right_index]:
                output[left_index + right_index] += left_value * right[right_index]
    return output


def compose(outer, inner, length):
    assert inner[0] == 0
    output = [0] * length
    power = [1] + [0] * (length - 1)
    order = next((index for index, value in enumerate(inner) if value), length)
    for exponent in range(min(len(outer), (length - 1) // order + 1)):
        if outer[exponent]:
            for index, value in enumerate(power):
                output[index] += outer[exponent] * value
        power = multiply(power, inner, length)
    return output


def residual(series, family, length):
    square = multiply(series, series, length)
    if family == 'A389474':
        inner = [2 * value for value in square]
        inner[2] += 1
        inner[3] += 2
        composition = compose(series, inner, length)
        return [composition[index] - 3 * square[index] for index in range(length)]
    cube = multiply(square, series, length)
    output = [-square[index] + 2 * cube[index] for index in range(length)]
    multiplier = 1 if family == 'A273095' else 3
    output[2] -= multiplier - 1
    for exponent in range(1, (length - 1) // 2 + 1):
        output[2 * exponent] += multiplier ** exponent * series[exponent]
    return output


def construct_nonlinear(family, degree):
    series = [0, 1] + [0] * degree
    for index in range(2, degree + 1):
        numerator = residual(series, family, index + 2)[index + 1]
        assert numerator % 2 == 0, (family, index, numerator)
        series[index] = numerator // 2
    assert all(value == 0 for value in residual(series, family, degree + 2))
    return series


def construct_linear(degree):
    series = [0, 1, 1] + [0] * (degree - 2)
    for index in range(3, degree + 1):
        series[index] = sum(
            series[exponent] * comb(exponent, index + 2 - 2 * exponent)
            for exponent in range(2, (index + 2) // 2 + 1)
            if 0 <= index + 2 - 2 * exponent <= exponent
        )
    return series


def substitute_cube(series, length):
    output = [0] * length
    for index in range((length - 1) // 3 + 1):
        output[3 * index] = series[index]
    return output


def construct_companion(degree):
    series = [0, 1] + [0] * (degree - 1)
    for index in range(2, degree + 1):
        series[index] = sum(
            series[exponent] * comb(exponent, index + 1 - 2 * exponent)
            for exponent in range(1, (index + 1) // 2 + 1)
            if 0 <= index + 1 - 2 * exponent <= exponent
        )
    return series


def inverse(series, length):
    assert series[:2] == [0, 1]
    reciprocal = [1] + [0] * (length - 1)
    for index in range(1, length - 1):
        reciprocal[index] = -sum(series[offset + 1] * reciprocal[index - offset]
                                 for offset in range(1, index + 1))
    power = [1] + [0] * (length - 1)
    output = [0] * length
    for exponent in range(1, length):
        power = multiply(power, reciprocal, length)
        assert power[exponent - 1] % exponent == 0
        output[exponent] = power[exponent - 1] // exponent
    variable = [0, 1] + [0] * (length - 2)
    assert compose(series, output, length) == variable
    assert compose(output, series, length) == variable
    return output


def companion_checks(first, second, third, companion, comparison, degree):
    length = degree + 1
    variable = [0, 1] + [0] * (length - 2)
    substitution = [0] * length
    substitution[2:4] = [1, 1]
    assert compose(companion, substitution, length) == [0] + companion[:degree]
    companion_square = multiply(companion, companion, length)
    assert third == [variable[index] + companion_square[index] for index in range(length)]
    product = variable
    iterate = variable
    factors = 0
    while any(iterate):
        factor = iterate.copy()
        factor[0] = 1
        product = multiply(product, factor, length)
        iterate_square = multiply(iterate, iterate, length)
        iterate_cube = multiply(iterate_square, iterate, length)
        iterate = [iterate_square[index] + iterate_cube[index] for index in range(length)]
        factors += 1
    assert product == companion
    seeds = [-2, 0, 1, 3]
    for seed in seeds:
        seeded = [variable[index] + seed * companion_square[index] for index in range(length)]
        assert seeded[2] == seed
        assert compose(seeded, substitution, length) == [0, 0, 1] + seeded[1:degree - 1]
        assert all(seeded[index] % 2 == 0 for index in range(3, length, 2))
        assert all(seeded[index] % 3 == 0 for index in range(5, length, 3))
    inverses = [inverse(series, length) for series in [first, second, third, companion, comparison]]
    inverse_first, inverse_second, inverse_third, inverse_companion, inverse_comparison = inverses
    first_square = multiply(inverse_first, inverse_first, length)
    first_cube = multiply(first_square, inverse_first, length)
    first_inner = [first_square[index] + 2 * first_cube[index] + 2 * int(index == 2)
                   for index in range(length)]
    assert compose(first, first_inner, length) == [3 * int(index == 2) for index in range(length)]
    triple_square = [3 * int(index == 2) for index in range(length)]
    assert compose(inverse_first, triple_square, length) == first_inner
    second_square = multiply(inverse_second, inverse_second, length)
    assert compose(second, [3 * value for value in second_square], length) == [
        2 * second_square[index] + int(index == 2) - 2 * int(index == 3) for index in range(length)]
    third_square = multiply(inverse_third, inverse_third, length)
    third_cube = multiply(third_square, inverse_third, length)
    assert compose(third, [third_square[index] + third_cube[index] for index in range(length)], length) == [
        third_square[index] + (third_square[index - 1] if index else 0) for index in range(length)]
    assert compose(inverse_companion, [0] + companion[:degree], length) == substitution
    twice_substitution = compose(substitution, substitution, length)
    substitution_square = multiply(substitution, substitution, length)
    factor = [0] * length
    factor[0] = factor[2] = 1
    for index in range(2, length):
        factor[index] += third[index - 2]
    assert compose(third, twice_substitution, length) == multiply(substitution_square, factor, length)
    comparison_polynomial = [0] * length
    comparison_polynomial[2:4] = [1, -2]
    inverse_square = multiply(inverse_comparison, inverse_comparison, length)
    assert compose(inverse_comparison, comparison_polynomial, length) == inverse_square
    inverse_power = inverse_comparison
    comparison_iterate = variable
    maximum_iteration = degree.bit_length()
    for iteration in range(maximum_iteration + 1):
        assert compose(comparison, inverse_power, length) == comparison_iterate
        inverse_power = multiply(inverse_power, inverse_power, length)
        comparison_iterate = compose(comparison_polynomial, comparison_iterate, length)
    catalan = [0] + [comb(2 * (index - 1), index - 1) // index for index in range(1, length)]
    catalan_square = multiply(catalan, catalan, length)
    assert catalan == [variable[index] + catalan_square[index] for index in range(length)]
    catalan_inner = [0] * length
    catalan_inner[2] = 1
    for index in range(1, length):
        catalan_inner[index] += 2 * catalan_square[index - 1]
    assert compose(catalan, catalan_inner, length) == catalan_square
    return {'product_factors': factors, 'integer_seeds': seeds,
            'reversion_series': 5, 'maximum_A273095_iteration': maximum_iteration,
            'identities_checked_through_degree': degree,
            'analytic_radius': 'Established by the written convergence and divergence proof.'}


def frobenius_checks(series, degree):
    length = degree + 1
    cube = multiply(multiply(series, series, length), series, length)
    substituted = substitute_cube(series, length)
    left = right = [1] + [0] * degree
    maximum = degree // 3 + 1
    for exponent in range(maximum + 1):
        assert all((left[index] - right[index]) % 3 == 0 for index in range(length))
        left = multiply(left, cube, length)
        right = multiply(right, substituted, length)
    return maximum


def main():
    parser = argparse.ArgumentParser(description='Exact coefficient checks for Hanna composition congruences.')
    parser.add_argument('--degree', type=int, default=96)
    arguments = parser.parse_args()
    degree = arguments.degree
    assert 43 <= degree <= 256
    data_path = Path(__file__).with_name('source_terms.json')
    data = json.loads(data_path.read_text())
    first = construct_nonlinear('A389474', degree)
    second = construct_nonlinear('A389475', degree)
    third = construct_linear(degree)
    companion = construct_companion(degree)
    comparison = construct_nonlinear('A273095', degree)
    sequences = {'A389474': first, 'A389475': second, 'A389472': third,
                 'A350432': companion, 'A273095': comparison}
    matched = {}
    for identifier, series in sequences.items():
        expected = data['entries'][identifier]['terms']
        assert series[1:len(expected) + 1] == expected, identifier
        matched[identifier] = len(expected)
    length = degree + 1
    first_square = multiply(first, first, length)
    assert first_square[2:4] == [1, 2]
    assert all(value % 9 == 0 for value in first_square[4:])
    polynomial = [0] * length
    polynomial[2:4] = [1, 2]
    left = right = [1] + [0] * degree
    for exponent in range(degree // 2 + 2):
        assert all((left[index] - right[index]) % 9 == 0 for index in range(length))
        left = multiply(left, first_square, length)
        right = multiply(right, polynomial, length)
    maximum_power = frobenius_checks(first, degree)
    assert frobenius_checks(second, degree) == maximum_power
    second_square = multiply(second, second, length)
    second_cube = multiply(second_square, second, length)
    second_substituted = substitute_cube(second, length)
    second_defect = [second_square[index] - 2 * second_substituted[index]
                     - int(index == 2) for index in range(length)]
    assert all(value % 3 == 0 for value in second_defect)
    assert all(second_square[index] == 2 * second_cube[index]
               for index in range(3, length, 2))
    assert all(second_square[2 * index] == 3 ** index * second[index]
               + 2 * second_cube[2 * index] for index in range(2, degree // 2 + 1))
    inner = [0] * length
    inner[2:4] = [1, 1]
    composition = compose(third, inner, length)
    assert composition == [0, 0, 1] + third[1:degree - 1]
    assert all(third[index] % 2 == 0 for index in range(3, length, 2))
    assert all(third[index] % 3 == 0 for index in range(5, length, 3))
    witnesses = {'A389474_square_degree_4': first_square[4],
                 'A389475_cube_minus_substitution_degree_4': second_cube[4] - second_substituted[4],
                 'A389475_square_defect_degree_4': second_defect[4],
                 'A389472_coefficient_3': third[3],
                 'A389472_coefficient_5': third[5]}
    assert witnesses == {'A389474_square_degree_4': 9,
                         'A389475_cube_minus_substitution_degree_4': 3,
                         'A389475_square_defect_degree_4': 15,
                         'A389472_coefficient_3': 2,
                         'A389472_coefficient_5': 6}
    companion_report = companion_checks(first, second, third, companion, comparison, degree)
    report = {'status': 'PASS', 'arithmetic': 'exact integers', 'maximum_degree': degree,
              'nonlinear_equations_checked_through_degree': degree + 1,
              'linear_equation_checked_through_degree': degree,
              'frobenius_exponents': [0, maximum_power],
              'square_power_mod_9_exponents': [0, degree // 2 + 1],
              'displayed_source_terms_matched': matched,
              'companion_checks': companion_report,
              'sharpness_witnesses': witnesses,
              'coverage': 'Finite coefficient identities and congruences supplement the all-index written proofs.',
              'source_terms_sha256': hashlib.sha256(data_path.read_bytes()).hexdigest(),
              'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
