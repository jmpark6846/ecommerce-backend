from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

import random
import string


class Command(BaseCommand):
    """
    This command will create a default Django admin superuser.
    """

    help = "Creates a Django user."

    def add_arguments(self, parser):
        parser.add_argument("arguments", nargs="*")

    def handle(self, *args, **options):
        # Gets the model for the current Django project's user.
        # This handles custom user models as well as Django's default.
        User = get_user_model()

        self.stdout.write(self.style.SUCCESS("Creating a new user..."))

        # If the command args are given -> try to create user with given args
        if options["arguments"]:
            try:
                user = User.objects.create_user(*options["arguments"])
                self.stdout.write(
                    self.style.SUCCESS(
                        'Created the user "{user}" with the given parameters.'.format(
                            user=user
                        )
                    )
                )
            except Exception as e:
                self.stdout.write(
                    "ERROR: Django returned an error when creating the user:"
                )
                self.stdout.write(str(e))
                self.stdout.write("")
                self.stdout.write(
                    "The arguments expected by the command are in this order:"
                )
                self.stdout.write(
                    str(User.objects.create.__code__.co_varnames[1:-1])
                )

        # or create default admin user
        else:
            pw = "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
            )
            user = User.objects.create(username="user", email="user@mysite.com")
            user.set_password(pw)
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    'Created user "user", email: "user@mysite.com", password: ' + pw
                )
            )
            self.stdout.write(
                self.style.SUCCESS("Log in and change this password immediately!")
            )