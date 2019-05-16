import folium
from folium import plugins
import geocoder
import requests
from branca.colormap import linear
import pandas as pd

# Leitura dos acidentes de transito
dados_datatran = []
for ii in range(2017,2020):
  csv = './dados/datatran' + str(ii) + '.csv'
  
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

def esta_no_padrao(geo, lat, lng):
    padrao_lat = lat in range ((int(geo.lat) - 5), (int(geo.lat) + 5))
    padrao_lng = lng in range ((int(geo.lng) - 7), (int(geo.lng) + 7))
    return not padrao_lat or not padrao_lng

# Estado com mais acidentes
uf_mais_aci = datatran_uf.loc[datatran_uf.total_acidentes == datatran_uf.total_acidentes.max(), :].uf.item()
uf_mais_aci_geo = geocoder.arcgis(uf_mais_aci + ", BR")

datatran_uf_mais_aci = datatran.loc[datatran['uf'] == uf_mais_aci, :].reset_index()

fora_padrao = []
for index, row in datatran_uf_mais_aci.iterrows():
    lat = int(row.latitude)
    lng = int(row.longitude)
    if esta_no_padrao(uf_mais_aci_geo, lat, lng):
        fora_padrao.append(index)

datatran_uf_mais_aci.drop(fora_padrao, inplace=True)

latslngs_mais_aci = list(zip(datatran_uf_mais_aci.latitude, datatran_uf_mais_aci.longitude))

# Estado com menos acidentes
uf_menos_aci = datatran_uf.loc[datatran_uf.total_acidentes == datatran_uf.total_acidentes.min(), :].uf.item()
uf_menos_aci_geo = geocoder.arcgis(uf_menos_aci + ", BR")

datatran_uf_menos_aci = datatran.loc[datatran['uf'] == uf_menos_aci, :].reset_index()

fora_padrao = []
for index, row in datatran_uf_menos_aci.iterrows():
    lat = int(row.latitude)
    lng = int(row.longitude)
    if esta_no_padrao(uf_menos_aci_geo, lat, lng):
        fora_padrao.append(index)

datatran_uf_menos_aci.drop(fora_padrao, inplace=True)

latslngs_menos_aci = list(zip(datatran_uf_menos_aci.latitude, datatran_uf_menos_aci.longitude))

# Criando o mapa
br = geocoder.arcgis("Brasil")

m = folium.Map(
    location=br.latlng,
    zoom_start=4,
    tiles='Stamen Terrain'
)

folium.Choropleth(geo_data=brazil_json, line_weight=2, fill_opacity=0, name='Marcação das UFs').add_to(m)

# Clusters de estado com mais acidentes
cluster_mais_aci = plugins.MarkerCluster(name='UF com mais acidentes', show=False).add_to(m)

for valor in latslngs_mais_aci:
  folium.Marker(valor).add_to(cluster_mais_aci) 

cluster_menos_aci = plugins.MarkerCluster(name='UF com menos acidentes', show=True).add_to(m)

for valor in latslngs_menos_aci:
  folium.Marker(valor).add_to(cluster_menos_aci) 

folium.LayerControl().add_to(m)

m.save('./mapas/clusters.html')