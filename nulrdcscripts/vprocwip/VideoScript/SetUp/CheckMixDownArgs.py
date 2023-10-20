from Arguments import args


def check_mixdown_arg():
    mixdown_list = ["copy", "4to3", "4to2", "2to1"]
    if not args.mixdown in mixdown_list:
        print("The selected audio mixdown is not a valid value")
        print("Please use one of the following: copy, 4to3, 4to2, 2to1")
        quit()
