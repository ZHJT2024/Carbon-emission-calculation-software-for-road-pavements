def calc_LQ_A1(p_ysb, f_jhl, kl_values, a_lqmh, a_lqhd, area):
    public_factor = a_lqmh * a_lqhd * area / 100000000.0
    ratio = p_ysb / 100.0
    denominator = 1 + ratio
    return ((ratio * f_jhl) / denominator + sum(kl_values) / denominator) * public_factor


def calc_LQ_A2(p_ysb, ys_kl_values, a_yj_jhl, a_lqmh, a_lqhd, area):
    public_factor = a_lqmh * a_lqhd * area / 100000000.0
    ratio = p_ysb / 100.0
    denominator = 1 + ratio
    return (sum(ys_kl_values) / denominator + (0.1040 * a_yj_jhl + 2.6571) * ratio / denominator) * public_factor


def calc_LQ_A3(a_lqmh, a_lqhd, area):
    public_factor = a_lqmh * a_lqhd * area / 100000000.0
    return 26.8 * public_factor


def calc_LQ_B1(a_lqmh, a_lqhd, area):
    public_factor = a_lqmh * a_lqhd * area / 100000000.0
    return 5.91 * public_factor


def calc_LQ_B2(a_lqmh, a_lqhd, area):
    public_factor = a_lqmh * a_lqhd * area / 100000000.0
    return 1.26 * public_factor


def calc_JC_A1(f_jc, a_jc, area):
    return f_jc * a_jc / 100.0 * area / 1000.0


def calc_JC_A2(a_yj_jc, a_jc, area):
    return (0.1023 * a_yj_jc + 0.3708) * 1.521 * a_jc / 100.0 * area / 1000.0


def calc_JC_B2(material_name, a_jc, area):
    if material_name == 'Cement-stabilized soil':
        if a_jc <= 20:
            return 0.3097479 * area / 1000.0
        return (309.7479 + (a_jc - 20) * 16.31901 * area / 1000.0) / 1000.0
    if material_name == 'Lime-stabilized soil':
        if a_jc <= 20:
            return 0.2897850 * area / 1000.0
        return (289.7850 + (a_jc - 20) * 12.67516 * area / 1000.0) / 1000.0
    if material_name == 'Lime-fly ash gravel':
        if a_jc <= 20:
            return 0.2930728 * area / 1000.0
        return (293.0728 + (a_jc - 20) * 16.31901 * area / 1000.0) / 1000.0
    return 0


def calc_GNC_A1(f_gnc, a_gnc, area, unit):
    if unit == 'cm':
        return f_gnc * a_gnc * area / 100000.0
    return f_gnc * a_gnc * area / 1000.0


def calc_GNC_A2(a_yj_gnc, a_gnc, area, unit):
    if unit == 'cm':
        return (0.1040 * a_yj_gnc + 2.6571) * 0.98 * a_gnc * area / 100.0
    return (0.1040 * a_yj_gnc + 2.6571) * 0.98 * a_gnc * area / 1000.0


def calc_D1(a_zhd, area):
    return 181.642 * a_zhd * area / 100000000.0


def calc_D2(a_zhd, area):
    return 3122.449 * a_zhd * area / 100000000.0
