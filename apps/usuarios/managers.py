from django.contrib.auth.base_user import BaseUserManager

class UsuarioManager(BaseUserManager):
    """Gerenciador customizado para o modelo Usuario (tb_usuario)."""

    def create_user(self, email, nome, password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail deve ser informado.')
        if not nome:
            raise ValueError('O nome deve ser informado.')

        email = self.normalize_email(email)
        user = self.model(email=email, nome=nome, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, password=None, **extra_fields):
        return self.create_user(email, nome, password=password, **extra_fields)
