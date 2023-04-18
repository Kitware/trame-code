import foo


async def bar():
    f = await foo()
    f_string = (
        f"Hooray {f}! format strings are not supported in current Monarch grammar"
    )
    return f_string
