from django import forms

class PagamentForm(forms.Form):
    sortida = forms.CharField(widget=forms.HiddenInput())
    check = forms.BooleanField(required=True, label="")
    Ds_MerchantParameters = forms.CharField(widget=forms.HiddenInput())
    Ds_Signature = forms.CharField(widget=forms.HiddenInput())
    acceptar_condicions = forms.BooleanField(required=True)

    def __init__(self, *args, **kwargs):
        super(PagamentForm, self).__init__(*args, **kwargs)
        self.sortida = kwargs.pop('sortida', None)
        self.Ds_MerchantParameters = kwargs.pop('Ds_MerchantParameters', None)
        self.Ds_Signature = kwargs.pop('signature', None)
        self.acceptar_condicions = kwargs.pop('signature', False)

