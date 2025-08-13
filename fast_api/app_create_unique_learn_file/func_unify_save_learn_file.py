def unify_save_inque_learn_file(learn_data_list: list) -> None:
    # print("###########################################################")
    # print("@@@@@@@ len(learn_data_list):", len(learn_data_list))
    learn_data_tuples_list = [tuple(cur_list) for cur_list in learn_data_list]
    unique_learn_data = list(set(learn_data_tuples_list))
    return unique_learn_data
    # print("@@@@@@@ len(unique_learn_data):", len(unique_learn_data))
    # print("###########################################################")
