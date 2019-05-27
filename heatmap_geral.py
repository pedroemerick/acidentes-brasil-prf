import folium
from folium import plugins
from folium.plugins import HeatMap
import geocoder
import requests
import pandas as pd

# Leitura dos acidentes de transito
dados_datatran = []
for ii in range(2017,2020):
  csv = './datasets/datatran' + str(ii) + '.csv'
  
  dado = pd.read_csv(csv, encoding = "ISO-8859-1", sep=';', engine='python', error_bad_lines=False)
  dados_datatran.append(dado)
  
datatran = pd.concat(dados_datatran, ignore_index=True)

# Cabeçalho generico para requisições web
headers = {
    'Content-Type': 'application/json;charset=UTF-8',
    'User-Agent': 'google-colab',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
}

response = requests.get("https://servicodados.ibge.gov.br/api/v2/malhas/"+
                        "?formato=application/vnd.geo+json&resolucao=2",
                       headers=headers)
brazil_json = response.json()

# Organizando dados para mapa
datatran_uf = pd.DataFrame(datatran.groupby('uf').size()).reset_index().rename(columns={0:'total_acidentes'})

response = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/estados",
                       headers=headers)
info_uf_data = response.json()

latslngs = list(zip(datatran.latitude, datatran.longitude))

# Criando o mapa
br = geocoder.arcgis("Brasil")

m = folium.Map(
    location=br.latlng,
    zoom_start=4,
    tiles='Stamen Terrain'
)

folium.Choropleth(geo_data=brazil_json, line_weight=2, fill_opacity=0, name='Marcação das UFs').add_to(m)

HeatMap(latslngs).add_to(m)

folium.LayerControl().add_to(m)

m.save('./mapas/heatmap_geral.html')