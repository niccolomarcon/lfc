import urwid as u

algorithms = [("Analyze Grammar", 'callback o boh'),
              ("Closure 1", 'ciaone')]


def algorithm_chosen(button, choice):
    global loop

    if choice == 'quit':
        raise u.ExitMainLoop
    else:
        loop.widget = u.Filler(u.Padding(u.Text("Not implemented")))


def create_start_menu():
    global loop
    body = [u.Divider()]

    for c in algorithms:
        b = u.Button(c[0], on_press=algorithm_chosen, user_data=c[1])
        body.append(u.AttrMap(b, None, focus_map='reversed'))  # Invert when focused

    body.extend([u.Divider(), u.Button('Quit', on_press=algorithm_chosen, user_data='quit')])
    return u.LineBox(
        u.Padding(u.ListBox(u.SimpleFocusListWalker(body)), right=2, left=2),
        'Choose an Algorithm'
    )


if __name__ == '__main__':
    # Show start menu
    main = create_start_menu()
    top = u.Overlay(create_start_menu(), u.SolidFill(' '), align='center', valign='middle', width=30, height=10)
    loop = u.MainLoop(top)
    loop.run()
