from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from .models import NTDdata
import pandas as pd
from django_pandas.io import read_frame
import json
import statsmodels.api as sm
from .forms import *
import numpy as np
from time import sleep


def index(request):
    form = YearForm()
    qs = NTDdata.objects.all()
    df = read_frame(qs)

    df['Date'] = pd.to_datetime(df["Date"])

    df['month'] = pd.DatetimeIndex(
        pd.to_datetime(df['Date'], format='%b')).month
    df['year'] = pd.DatetimeIndex(pd.to_datetime(df['Date'], format='%Y')).year
    df = df.sample(frac=0.7, random_state=42)
    df.reset_index()
    df = df.sort_values(by='Date')
    ResumenData = df.groupby(['year', 'month']).agg({
        'Close': 'mean',
        'High': 'max',
        'Low': 'min'
    }).reset_index().rename(columns={'Close': 'Promedio de cierre', 'High': 'Maximo', 'Low': 'Minimo', 'month': 'Mes', 'year': 'Año'})
    ResumenData['Crecimiento'] = ResumenData['Promedio de cierre'].pct_change()
    dfbplot = df.groupby(['year', 'month']).agg(
        {'Close': 'mean'}).reset_index()
    dfbplot.year.astype(str)
    dfbplot.month.astype(str)
    dfbplot = dfbplot[['Close', 'year']].rename(
        columns={'Close': 'value', 'year':  "name"})
    dfbplot = dfbplot.pivot(columns='name', values='value')
    dfbplot = dfbplot.apply(lambda x: pd.Series(x.dropna().values))

    dfbplotvalues = dfbplot.T.values.tolist()
    dfbplotnames = dfbplot.columns.tolist()
    dfbplotvalues = np.where(np.isnan(dfbplotvalues), np.nan, dfbplotvalues)
    dfbplotvalues = [[valor for valor in sublista if not np.isnan(
        valor)] for sublista in dfbplotvalues]

    model = sm.tsa.SARIMAX(df.Close, order=(
        2, 0, 1), seasonal_order=(2, 1, 0, 12))
    model_fit = model.fit()
    y2 = model_fit.forecast(steps=15)
    start_date = df['Date'].max() + pd.DateOffset(days=1)
    end_date = df['Date'].max() + pd.DateOffset(days=15)
    date_range = pd.date_range(start=start_date, end=end_date)
    futuro = pd.DataFrame({'Date': date_range, 'Close': y2})

    if request.method == 'POST':
        form = YearForm(request.POST)

    # Check if the form is valid:
        if form.is_valid():
            SelecYear = form.cleaned_data['Select_Year']
            ResumenData = ResumenData.query(f"Año=={SelecYear}")
            piedata = ResumenData[['Promedio de cierre', 'Mes']].rename(
                columns={'Promedio de cierre': 'value', 'Mes':  "name"})
            piedata['name'] = piedata['name'].astype(str)
            piedata['name'] = piedata['name'].replace(
                {'1': 'enero',
                 '2': 'febrero',
                 '3': 'marzo',
                 '4': 'abril',
                 '5': 'mayo',
                 '6': 'junio',
                 '7': 'julio',
                 '8': 'agosto',
                 '9': 'septiembre',
                 '10': 'octubre',
                 '11': 'noviembre',
                 '12': 'diciembre'})
            piedata = piedata.to_dict(orient='records')
            ctx = {
                'form': form,
                "Ndata": ResumenData.idxmax()[1],
                "MeanCloseData": round(ResumenData['Promedio de cierre'].mean(), 4),
                "MaxCloseData": round(ResumenData['Maximo'].max(), 4),
                "MinCloseData": round(ResumenData['Minimo'].min(), 4),
                'table_data': ResumenData.to_html(table_id="test",
                                                  classes=[
                                                      "table", "table-bordered", "table-striped", "dataTable", "dtr-inline"],
                                                  index=False,
                                                  justify='center',
                                                  formatters={'Close': lambda x: '$ ' + str(x),
                                                              'High': lambda x: '$ ' + str(x),
                                                              'Low': lambda x: '$ ' + str(x),
                                                              }
                                                  ),
                "EchartData1X": df.Date.dt.strftime('%Y-%m-%d').tolist(),
                "EchartData1Y": df.Close.tolist(),
                "EchartData1XF": futuro.Date.dt.strftime('%Y-%m-%d').tolist(),
                "EchartData1YF": futuro.Close.tolist(),
                'EchartData2': piedata,
                'EchartDataBoxName': dfbplotnames,
                'EchartDataBoxValue': dfbplotvalues
            }
        else:
            pass
    else:
        form = YearForm()
        piedata = ResumenData[['Promedio de cierre', 'Mes']].rename(
            columns={'Promedio de cierre': 'value', 'Mes':  "name"})
        piedata['name'] = piedata['name'].astype(str)
        piedata['name'] = piedata['name'].replace(
            {'1': 'enero',
             '2': 'febrero',
             '3': 'marzo',
             '4': 'abril',
             '5': 'mayo',
             '6': 'junio',
             '7': 'julio',
             '8': 'agosto',
             '9': 'septiembre',
             '10': 'octubre',
             '11': 'noviembre',
             '12': 'diciembre'})
        piedata = piedata.to_dict(orient='records')
        ctx = {
            'form': form,
            "Ndata": df.idxmax()[1],
            "MeanCloseData": round(df.Close.mean(), 4),
            "MaxCloseData": round(df.Close.max(), 4),
            "MinCloseData": round(df.Close.min(), 4),
            'table_data': ResumenData.to_html(table_id="test",
                                              classes=[
                                                  "table", "table-bordered", "table-striped", "dataTable", "dtr-inline"],
                                              index=False,
                                              justify='center',
                                              formatters={'Close': lambda x: '$ ' + str(x),
                                                          'High': lambda x: '$ ' + str(x),
                                                          'Low': lambda x: '$ ' + str(x),
                                                          }
                                              ),
            "EchartData1X": df.Date.dt.strftime('%Y-%m-%d').tolist(),
            "EchartData1Y": df.Close.tolist(),
            "EchartData1XF": futuro.Date.dt.strftime('%Y-%m-%d').tolist(),
            "EchartData1YF": futuro.Close.tolist(),
            'EchartData2': piedata,
            'EchartDataBoxName': dfbplotnames,
            'EchartDataBoxValue': dfbplotvalues
        }

    return render(request, "home.html", ctx)
