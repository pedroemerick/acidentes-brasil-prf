import folium
import geocoder
import requests
from branca.colormap import linear
import pandas as pd

# print(folium.__version__)
# print(requests.__version__)
# print(geocoder.__version__)

dados_datatran = []
for ii in range(2017,2020):
  csv = './dados/datatran' + str(ii) + '.csv'
  
  dado = pd.read_csv(csv, encoding = "ISO-8859-1", sep=';', engine='python', error_bad_lines=False)
  dados_datatran.append(dado)
  
datatran = pd.concat(dados_datatran, ignore_index=True)

# meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
meses = ['jan', 'fev', 'mar']
dados_infra = []
for mes in meses:
  # csv = './dados/2017/' + str(mes) + '.csv'
  # dado = pd.read_csv(csv, encoding = "ISO-8859-1", sep=',', engine='python', error_bad_lines=False)
  # dados_infra.append(dado)

  csv = './dados/2018/' + str(mes) + '.csv'
  dado = pd.read_csv(csv, encoding = "ISO-8859-1", sep=',', engine='python', error_bad_lines=False)
  dados_infra.append(dado)
  
datainfra = pd.concat(dados_infra, ignore_index=True)

print(datainfra.head())

# datatran.head()

# configure a generical header
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

# brazil_json

# datatran.uf.unique()

datatran_uf = pd.DataFrame(datatran.groupby('uf').size()).reset_index().rename(columns={0:'total_acidentes'})
datainfra_uf = pd.DataFrame(datainfra.groupby('uf_infracao').size()).reset_index().rename(
  columns={'uf_infracao':'uf', 0:'total_infracoes'})

print(datainfra_uf.head())

response = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/estados",
                       headers=headers)
info_uf_data = response.json()

for lista in info_uf_data:
  datatran_uf.loc[datatran_uf.uf == lista['sigla'], 'nome'] = lista['nome']
  datatran_uf.loc[datatran_uf.uf == lista['sigla'], 'codarea'] = lista['id']

  datainfra_uf.loc[datainfra_uf.uf == lista['sigla'], 'nome'] = lista['nome']
  datainfra_uf.loc[datainfra_uf.uf == lista['sigla'], 'codarea'] = lista['id']

datatran_uf.set_index('codarea',inplace=True)
datatran_uf.index.name = None
datatran_uf["codarea"] = datatran_uf.index
# datatran_uf.head()

datainfra_uf.set_index('codarea',inplace=True)
datainfra_uf.index.name = None
datainfra_uf["codarea"] = datatran_uf.index
print(datainfra_uf.head())

colormap = linear.YlOrRd_03.scale(
    datatran_uf.total_acidentes.min(),
    datatran_uf.total_acidentes.max())

colormap.caption="Acidentes em Rodovias Federais"

colormap2 = linear.YlGnBu_03.scale(
    datainfra_uf.total_infracoes.min(),
    datainfra_uf.total_infracoes.max())

colormap2.caption="Infrações de Trânsito em Rodovias Federais"

# print(colormap(5000.0))

# colormap

for uf in brazil_json['features']:
  codarea_aux = int(uf['properties']['codarea'])
  uf['properties']['total_acidentes'] = str(datatran_uf.loc[codarea_aux,'total_acidentes'])
  uf['properties']['total_infracoes'] = str(datainfra_uf.loc[codarea_aux,'total_infracoes'])
  uf['properties']['nome'] = str(datatran_uf.loc[codarea_aux,'nome'])


br = geocoder.arcgis("Brasil")

# Create a map object
m = folium.Map(
    location=br.latlng,
    zoom_start=4,
    tiles='Stamen Terrain'
)
    
# Create a Choropleth using folium.GeoJson()
folium.GeoJson(brazil_json,
               name='Total de Acidentes em Rodovias Federais',
               style_function=lambda x: {'fillColor': colormap(datatran_uf.loc[int(x['properties']['codarea']),
                                                                           "total_acidentes"]),
                                         'color': 'black','weight':2, 'fillOpacity':0.8},
               tooltip=folium.GeoJsonTooltip(fields=['nome','total_acidentes'], 
                                            aliases=['Estado:','Total de Acidentes:'], 
                                            localize=True)
              ).add_to(m)

folium.GeoJson(brazil_json,
               name='Total de Infrações em Rodovias Federais',
               style_function=lambda x: {'fillColor': colormap(datainfra_uf.loc[int(x['properties']['codarea']),
                                                                           "total_infracoes"]),
                                         'color': 'black','weight':2, 'fillOpacity':0.8},
               tooltip=folium.GeoJsonTooltip(fields=['nome','total_infracoes'], 
                                            aliases=['Estado:','Total de Infrações:'], 
                                            localize=True),
                show=False
              ).add_to(m)

# Add a LayerControl.
folium.LayerControl().add_to(m)

# And the Color Map legend.
colormap.add_to(m)
colormap2.add_to(m)

m.save('index.html')

# response = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/regioes",
#                        headers=headers)
# regioes = response.json()

# regioes

# response = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/estados",
#                        headers=headers)
# info_uf_data = response.json()

# info_uf_data



# norte = []
# nordeste = []
# sudeste = []
# sul = []
# centro_oeste = []

# for lista in info_uf_data:
#   if(lista['regiao']['nome'] == 'Nordeste'):
#     nordeste.append(lista['sigla'])
#   elif(lista['regiao']['nome'] == 'Norte'):
#     norte.append(lista['sigla'])
#   elif(lista['regiao']['nome'] == 'Sudeste'):
#     sudeste.append(lista['sigla'])
#   elif(lista['regiao']['nome'] == 'Sul'):
#     sul.append(lista['sigla'])
#   elif(lista['regiao']['nome'] == 'Centro-Oeste'):
#     centro_oeste.append(lista['sigla'])

# nordeste

# latlng = zip(datatran.loc[datatran['uf'] == 'MG', :].latitude, datatran.loc[datatran['uf'] == 'MG', :].longitude)

# for value in latlng:
#   teste = list(value)
#   print (teste)

# datatran.loc[datatran['uf'] == 'MG', :].head()

# import numpy as np
# from folium import plugins
# import geocoder

# br = geocoder.arcgis("Brasil")

# # Create a map
# m = folium.Map(
#     location=br.latlng,
#     zoom_start=4,
#     tiles='Stamen Terrain',
#     width='75%',
#     height='75%'
# )

# folium.GeoJson(brazil_json).add_to(m)

# regioes = [nordeste, norte, sudeste, sul, centro_oeste]

# # #for uf in names_uf:
# #   # create a cluster
# # cluster = plugins.MarkerCluster().add_to(m)
# # latlng = zip(datatran.loc[datatran['uf'] == 'RN', :].latitude, datatran.loc[datatran['uf'] == 'RN', :].longitude)
  
# # for value in latlng:
# #   # discovery the latitude and longiture for city
# # #     g = geocoder.arcgis(city + " RN")
# #   folium.Marker(value).add_to(cluster)

# # teste = ['RN', 'BA']

# # for uf in nordeste:
# #   # create a cluster
# #   cluster = plugins.MarkerCluster().add_to(m)
# #   latlng = zip(datatran.loc[datatran['uf'] == uf, :].latitude, datatran.loc[datatran['uf'] == uf, :].longitude)
 
# #   for value in latlng:
# #     # discovery the latitude and longiture for city
# #     #g = geocoder.arcgis(city + " RN")
# #     folium.Marker(value).add_to(cluster) 

# cluster = plugins.MarkerCluster(control=False).add_to(m)

# nordeste_clus = folium.plugins.FeatureGroupSubGroup(cluster, 'Nordeste')
# norte_clus = folium.plugins.FeatureGroupSubGroup(cluster, 'Norte')
# sudeste_clus = folium.plugins.FeatureGroupSubGroup(cluster, 'Sudeste')
# sul_clus = folium.plugins.FeatureGroupSubGroup(cluster, 'Sul')
# centro_oeste_clus = folium.plugins.FeatureGroupSubGroup(cluster, 'Centro-Oeste')

# intra_clusters = [nordeste_clus, norte_clus, sudeste_clus, sul_clus, centro_oeste_clus]

# # add intra-cluster to map
# m.add_child(nordeste_clus)
# m.add_child(norte_clus)
# m.add_child(sudeste_clus)
# m.add_child(sul_clus)
# m.add_child(centro_oeste_clus)

# index = 0
# for regiao in regioes:
#   for uf in regiao:
#     # discovery the latitude and longiture for city
# #     g = geocoder.arcgis(city + " RN")
#     latlng = zip(datatran.loc[datatran['uf'] == uf, :].latitude, datatran.loc[datatran['uf'] == uf, :].longitude)
 
#     for value in latlng:
#       # discovery the latitude and longiture for city
#       #g = geocoder.arcgis(city + " RN")
#       folium.Marker(value).add_to(intra_clusters[index]) 

#   index += 1

# folium.LayerControl(collapsed=False).add_to(m)

# m.save('index.html')

# teste = zip(datatran.loc[datatran['br'] == 116, :].latitude, datatran.loc[datatran['br'] == 116, :].longitude)

# len(datatran.br.unique())

# lista = []
# for value in teste:
#   lista.append(value)

# lista

# import numpy as np
# from folium import plugins
# import geocoder

# br = geocoder.arcgis("Brasil")

# # Create a map
# m = folium.Map(
#     location=br.latlng,
#     zoom_start=4,
#     tiles='Stamen Terrain',
#     width='75%',
#     height='75%'
# )

# cluster = plugins.MarkerCluster().add_to(m)

# for valor in lista:
#   # create a cluster
#   folium.Marker(valor).add_to(cluster) 

# m