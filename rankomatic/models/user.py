import os
import hashlib

from rankomatic import db


class User(db.DynamicDocument):
    """A user of the application, has a name, salted password digest, salt, and a
    list of Datasets belonging to the user.

    """
    username = db.StringField(required=True, max_length=255)
    password_digest = db.StringField(required=True)
    salt = db.StringField(required=True)
    dset_names = db.ListField(db.StringField(), default=lambda: [])

    def set_password(self, password):
        """Adds a randomly generated salt to the User, then appends it to the
        password before hashing it, then saves the digest.

        """
        self.salt = os.urandom(64).encode('hex')
        h = hashlib.sha512()
        password += self.salt
        h.update(password)
        self.password_digest = h.hexdigest()

    def is_password_valid(self, guess):
        """Appends the user's salt to the guess before hashing it, then compares
        it with the stored password digest.

        """
        h = hashlib.sha512()
        guess += self.salt
        h.update(guess)
        return h.hexdigest() == self.password_digest
