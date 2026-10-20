from django.contrib import admin
from django import forms
from .models import Usuario, Aluno

class UsuarioAdminForm(forms.ModelForm):
    senha_plana = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput,
        required=False,
        help_text="Deixe em branco para manter a senha atual. Digite uma nova senha para alterá-la."
    )

    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'senha_plana']

    def save(self, commit=True):
        usuario = super().save(commit=False)
        senha_plana = self.cleaned_data.get('senha_plana')
        if senha_plana:
            usuario.set_password(senha_plana)
        elif not usuario.password:
            usuario.set_unusable_password()
        if commit:
            usuario.save()
        return usuario


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    form = UsuarioAdminForm
    list_display = ('id_usuario', 'nome', 'email')
    search_fields = ('nome', 'email')
    ordering = ('nome',)
    fields = ('nome', 'email', 'senha_plana')


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('id_aluno', 'usuario', 'curso', 'matricula')
    search_fields = ('usuario__nome', 'usuario__email', 'matricula')
    list_filter = ('curso__instituicao', 'curso')
    autocomplete_fields = ('usuario', 'curso')
    ordering = ('usuario__nome',)
