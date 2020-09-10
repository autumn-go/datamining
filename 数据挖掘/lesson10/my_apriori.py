# -*- coding: utf-8 -*-

# apriori算法的一个简单实现
from sys import exit, exc_info
from itertools import combinations
from collections import defaultdict
from time import clock
from optparse import OptionParser


def parse_arguments(parser):
    '''
        解析命令行给定的参数，运行apriori算法
    '''
    parser.add_option('-i', '--input', type='string', help='input file',
                      dest='input')
    parser.add_option('-s', '--support', type='float', help='min support',
                      dest='support')
    parser.add_option('-c', '--confidence', type='float',
                      help='min confidence', dest='confidence')

    (options, args) = parser.parse_args()
    if not options.input:
        parser.error('Input filename not given')
    if not options.support:
        parser.error('Support not given')
    if not options.confidence:
        parser.error('Confidence not given')
    return(options, args)


def get_transactions_from_file(file_name):
    '''
        读取文件，返回所有“购物篮”的结果
        返回的格式是list，其中每个元素都是一个“购物篮”中的“商品”组成的frozenset
    '''
    try:
        with open(file_name) as f:
            content = f.readlines()
            f.close()
    except IOError as e:
        print 'I/O error({0}): {1}'.format(e.errno, e.strerror)
        exit()
    except:
        print 'Unexpected error: ', exc_info()[0]
        exit()
    transactions = []
    for line in content:
        transactions.append(frozenset(line.strip().split()))
    return transactions


def print_results(itemsets_list, rules, transactions):
    '''
        输出结果
    '''
    for idx, itemsets in enumerate(itemsets_list):
        if len(itemsets) == 0:
            continue
        print 'Itemsets of size', idx + 1
        formatted_itemsets = []
        for itemset, freq in itemsets.iteritems():
            support = float(freq) / len(transactions)
            formatted_itemsets.append((','.join(sorted(map(str, itemset))),
                                       round(support, 3)))
        sorted_itemsets = sorted(formatted_itemsets,
                                 key=lambda tup: (-tup[1], tup[0]))
        for itemset, support in sorted_itemsets:
            print itemset, '{0:.3f}'.format(support)

        print

    print 'RULES'
    formatted_rules = [(','.join(sorted(map(str, rule[0]))) + ' -> ' +
                        ','.join(sorted(map(str, rule[1]))),
                       round(acc, 3))
                       for rule, acc in rules]
    sorted_rules = sorted(formatted_rules, key=lambda tup: (-tup[1], tup[0]))
    for rule, acc in sorted_rules:
        print rule, '{0:.3f}'.format(acc)


def remove_itemsets_without_min_support(itemsets, min_sup, transactions):
    '''
        删除不满足最小支持度的itemsets
    '''
    for itemset, freq in itemsets.items():
        if float(freq) / len(transactions) < min_sup:
                del itemsets[itemset]


def generate_itemsets(itemsets_list, min_sup):
    '''
        给定1-项集，这个函数会通过和自己join生成itemsets，然后删除不满足最小支持度的itemsets
        参数：
        1）itemsets_list: 一个包含1-项集的list
        2）min_sup：最小支持度
    '''
    try:
        next_candidate_item_sets = self_join(itemsets_list[0])
    except IndexError:
        return
    while(len(next_candidate_item_sets) != 0):
        itemsets_list.append(defaultdict(int))
        for idx, item_set in enumerate(next_candidate_item_sets):
            for transaction in transactions:
                if item_set.issubset(transaction):
                    itemsets_list[-1][item_set] += 1

        remove_itemsets_without_min_support(itemsets_list[-1], min_sup,
                                            transactions)
        try:
            next_candidate_item_sets = self_join(itemsets_list[-1])
        except IndexError:
            break


def build_k_minus_one_members_and_their_occurrences(itemsets, k):

    k_minus_one_members_and_occurrences = defaultdict(list)
    for itemset in itemsets:
        # small cheat to make a list a hashable type
        k_minus_one_members = ''.join(sorted(itemset)[:k - 1])
        k_minus_one_members_and_occurrences[k_minus_one_members].\
            append(itemset)
    return k_minus_one_members_and_occurrences


def generate_itemsets_from_kmomo(kmomo):

    new_itemsets = []
    for k_minus_one_members, occurrences in kmomo.items():
        if len(occurrences) < 2:
            # delete those k_minus_one_members that have only one occurrence
            del kmomo[k_minus_one_members]
        else:  # generate the new itemsets
            for combination in combinations(occurrences, 2):
                union = combination[0].union(combination[1])
                new_itemsets.append(union)
    return new_itemsets


def self_join(itemsets):

    itemsets = itemsets.keys()  # we are only interested on the itemsets
                                # themselves, not the frequencies
    k = len(itemsets[0])  # length of the itemsets
    # making sure all the itemsets have the same length
    assert(all(len(itemset) == k for itemset in itemsets))
    kmomo = build_k_minus_one_members_and_their_occurrences(itemsets, k)
    return generate_itemsets_from_kmomo(kmomo)


def build_one_consequent_rules(itemset, freq, itemsets_list):

    accurate_consequents = []
    rules = []
    for combination in combinations(itemset, 1):
        consequent = frozenset(combination)
        antecedent = itemset - consequent
        ant_len_itemsets = itemsets_list[len(antecedent) - 1]
        conf = float(freq) / ant_len_itemsets[antecedent]
        if conf >= min_conf:
            accurate_consequents.append(consequent)
            rules.append(((antecedent, consequent), conf))
    return accurate_consequents, rules


def build_n_plus_one_consequent_rules(itemset, freq, accurate_consequents,
                                      itemsets_list):

    rules = []
    consequent_length = 2
    while(len(accurate_consequents) != 0 and
          consequent_length < len(itemset)):
        new_accurate_consequents = []
        for combination in combinations(accurate_consequents, 2):
            consequent = frozenset.union(*combination)
            if len(consequent) != consequent_length:
                # combined itemsets must share n-1 common items
                continue
            antecedent = itemset - consequent
            ant_len_itemsets = itemsets_list[len(antecedent) - 1]
            conf = float(freq) / ant_len_itemsets[antecedent]
            if conf >= min_conf:
                new_accurate_consequents.append(consequent)
                rules.append(((antecedent, consequent), conf))
        accurate_consequents = new_accurate_consequents
        consequent_length += 1
    return rules


def generate_rules(itemsets, min_conf, itemsets_list):
    '''
        参数
        1)itemsets: 用于生成规则的相同长度的itemsets
        2)min_conf: 最小信任度
        3)itemsets_list: 相同长度的itemsets组成的字典
        返回结果
        4)返回的规则: 规则是这样的格式为 [((antecedent, consequent), confidence), ...]
    '''
    rules = []
    for itemset, freq in itemsets.iteritems():
        accurate_consequents, new_rules = \
            build_one_consequent_rules(itemset, freq, itemsets_list)
        rules += new_rules
        # 如果现在itemset大小已经小于1，直接continue
        if len(itemset) <= 2:
            continue

        rules += build_n_plus_one_consequent_rules(itemset, freq,
                                                   accurate_consequents,
                                                   itemsets_list)
    return list(set(rules))


if __name__ == '__main__':
    usage_text = 'Usage: %prog -s minsup -c minconf [-a minatm]'
    parser = OptionParser(usage=usage_text)
    (options, args) = parse_arguments(parser)
    min_sup = options.support
    min_conf = options.confidence
    t1 = clock()

    transactions = get_transactions_from_file(options.input)
    itemsets_list = [defaultdict(int)]

    # 生成长度为1的itemsets
    for transaction in transactions:
        for item in transaction:
            itemsets_list[0][frozenset([item])] += 1
    remove_itemsets_without_min_support(itemsets_list[0], min_sup,
                                        transactions)

    # 生成长度>1的itemsets
    generate_itemsets(itemsets_list, min_sup)

    # 生成规则
    rules = []
    for itemsets in list(reversed(itemsets_list))[:-1]:
        rules += generate_rules(itemsets, min_conf, itemsets_list)

    t2 = clock()
    print_results(itemsets_list, rules, transactions)
