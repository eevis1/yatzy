def calculate_score(dice, category):
    if category == 'ykkoset':
        return dice.count(1) * 1
    elif category == 'kakkoset':
        return dice.count(2) * 2
    elif category == 'kolmoset':
        return dice.count(3) * 3
    elif category == 'neloset':
        return dice.count(4) * 4
    elif category == 'vitoset':
        return dice.count(5) * 5
    elif category == 'kutonen':
        return dice.count(6) * 6
    elif category == 'pari':
        pairs = [d for d in set(dice) if dice.count(d) >= 2]
        if pairs:
            return max(pairs) * 2
        else:
            return 0
    elif category == 'kaksi_paria':
        pairs = [d for d in set(dice) if dice.count(d) >= 2]
        if len(pairs) >= 2:
            return sum(sorted(pairs, reverse=True)[:2]) * 2
        else:
            return 0
    elif category == 'kolme_samaa':
        for d in set(dice):
            if dice.count(d) >= 3:
                return d * 3
        return 0
    elif category == 'nelja_samaa':
        for d in set(dice):
            if dice.count(d) >= 4:
                return d * 4
        return 0
    elif category == 'pieni_suora':
        return 15 if sorted(dice) == [1, 2, 3, 4, 5] else 0
    elif category == 'iso_suora':
        return 20 if sorted(dice) == [2, 3, 4, 5, 6] else 0
    elif category == 'tayskasi':
        three_of_a_kind = None
        pair = None
        for d in set(dice):
            if dice.count(d) == 3:
                three_of_a_kind = d
            elif dice.count(d) == 2:
                pair = d
        return (three_of_a_kind * 3 + pair * 2) if three_of_a_kind and pair else 0
    elif category == 'yatzy':
        return 50 if len(set(dice)) == 1 else 0
    elif category == 'sattuma':
        return sum(dice)
    else:
        return 0