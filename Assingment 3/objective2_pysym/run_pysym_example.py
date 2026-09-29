import pySym


def main():
    project = pySym.Project("./test.py")
    path_group = project.factory.path_group()
    path_group.explore()

    print(path_group)
    if not path_group.completed:
        print("No completed paths were found.")
        return

    final_state = path_group.completed[0].state
    print("Computed z =", final_state.any_int("z"))


if __name__ == "__main__":
    main()
