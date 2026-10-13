

## mapping dividing results
## onto the UI display format

# from divide.resources.CONFIG import *


# classes_final # CNN + rule-based 최종 결과


def assort_by_test(page_labels):
    classes = set(page_labels)

    test_labels_dict = dict(zip(classes, [[] for i in range(len(classes))]))

    for page, page_label in enumerate(page_labels):
        page_list = test_labels_dict[page_label]
        page_list.append(page)
        test_labels_dict[page_label] = page_list

    return test_labels_dict # {'시험이름': [pages (index 기준) <list>]}



def ui_postprocess(is_extractable, divided_dict, tests_displayed, tests_activated):

    test_info_formatted = dict(zip(tests_displayed,
                                   [{'active': 0, 'extractable': 1, 'pages_id': []} for i in range(len(tests_displayed))]))

    for test_ui in tests_displayed:

        # active 처리
        if test_ui in tests_activated:
            test_info_formatted[test_ui]['active'] = 1

        # pages 처리: 분류 결과 중 해당 시험의 페이지
        pages_index = sorted(divided_dict.get(test_ui, []))
        test_info_formatted[test_ui]['pages_id'] = [p_id for p_id in pages_index]

        # extractable 처리
        pages = test_info_formatted[test_ui]['pages_id']
        for page in pages:
            if is_extractable[page-1] == 0:
                test_info_formatted[test_ui]['extractable'] = 0
                break

    return test_info_formatted
