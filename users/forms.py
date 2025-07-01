from django import forms


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(
        widget=forms.PasswordInput()
    )


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {
                'class': 'form-control ',
                'id': 'username',
                'placeholder': "votre nom d'utilisateur",
            }
        )
        self.fields['password'].widget.attrs.update(
            {
                'class': 'form-control',
                'id': "password",
                'type': 'password',
                'placeholder': 'Mot de passe',
                'data-password-input': 'data-password-input',
            }
        )
