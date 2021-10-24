from invoke import task


@task
def wait_for(ctx, host, timeout=30):
    ctx.run(f"wait-for-it {host} --timeout={timeout}")


@task
def makemigrations(ctx):
    ctx.run("python manage.py makemigrations")


@task
def migrate(ctx, noinput=False):
    options = []
    if noinput:
        options.append("--noinput")

    options = " ".join(options)
    ctx.run(f"python manage.py migrate {options}")


@task
def runserver(ctx, host="0.0.0.0", port=8000):
    command = f"python manage.py runserver {host}:{port}"
    ctx.run(command, pty=True)
