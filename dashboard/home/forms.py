from django import forms
from .models import NTDdata
import pandas as pd
from django_pandas.io import read_frame


class YearForm(forms.Form):
    qs = NTDdata.objects.all()
    df = read_frame(qs)
    df['Date'] = pd.to_datetime(df["Date"])

    df['month'] = pd.DatetimeIndex(
        pd.to_datetime(df['Date'], format='%b')).month
    df['year'] = pd.DatetimeIndex(pd.to_datetime(df['Date'], format='%Y')).year
    CATEGORIAS_CHOICES = [(str(anio), str(anio)) for anio in df.year.unique()]
    Select_Year = forms.ChoiceField(choices=sorted(CATEGORIAS_CHOICES, reverse=True),
                                    required=False,
                                    label='',
                                    widget=forms.Select(attrs={'class': 'form-control'}
                                                        ))
