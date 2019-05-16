import folium
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

# Leitura das infrações
# # meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
# meses = ['jan', 'fev', 'mar']
# dados_infra = []
# for mes in meses:
#   # csv = './dados/2017/' + str(mes) + '.csv'
#   # dado = pd.read_csv(csv, encoding = "ISO-8859-1", sep=',', engine='python', error_bad_lines=False)
#   # dados_infra.append(dado)

#   csv = './dados/2018/' + str(mes) + '.csv'
#   dado = pd.read_csv(csv, encoding = "ISO-8859-1", sep=',', engine='python', error_bad_lines=False)
#   dados_infra.append(dado)
  
# datainfra = pd.concat(dados_infra, ignore_index=True)

# print(datainfra.head())

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
# datainfra_uf = pd.DataFrame(datainfra.groupby('uf_infracao').size()).reset_index().rename(
# columns={'uf_infracao':'uf', 0:'total_infracoes'})

# print(datainfra_uf.head())

response = requests.get("https://servicodados.ibge.gov.br/api/v1/localidades/estados",
                       headers=headers)
info_uf_data = response.json()

for lista in info_uf_data:
  datatran_uf.loc[datatran_uf.uf == lista['sigla'], 'nome'] = lista['nome']
  datatran_uf.loc[datatran_uf.uf == lista['sigla'], 'codarea'] = lista['id']

  # datainfra_uf.loc[datainfra_uf.uf == lista['sigla'], 'nome'] = lista['nome']
  # datainfra_uf.loc[datainfra_uf.uf == lista['sigla'], 'codarea'] = lista['id']

datatran_uf.set_index('codarea',inplace=True)
datatran_uf.index.name = None
datatran_uf["codarea"] = datatran_uf.index

# datainfra_uf.set_index('codarea',inplace=True)
# datainfra_uf.index.name = None
# datainfra_uf["codarea"] = datatran_uf.index
# print(datainfra_uf.head())

colormap = linear.YlOrRd_03.scale(
    datatran_uf.total_acidentes.min(),
    datatran_uf.total_acidentes.max())

colormap.caption="Acidentes em Rodovias Federais"

# colormap2 = linear.YlGnBu_03.scale(
#     datainfra_uf.total_infracoes.min(),
#     datainfra_uf.total_infracoes.max())

# colormap2.caption="Infrações de Trânsito em Rodovias Federais"

for uf in brazil_json['features']:
  codarea_aux = int(uf['properties']['codarea'])
  uf['properties']['total_acidentes'] = str(datatran_uf.loc[codarea_aux,'total_acidentes'])
  # uf['properties']['total_infracoes'] = str(datainfra_uf.loc[codarea_aux,'total_infracoes'])
  uf['properties']['nome'] = str(datatran_uf.loc[codarea_aux,'nome'])


br = geocoder.arcgis("Brasil")

# Cria o mapa
m = folium.Map(
    location=br.latlng,
    zoom_start=4,
    tiles='Stamen Terrain'
)
    
# Cria o Choropleth usando folium.GeoJson()
folium.GeoJson(brazil_json,
               name='Total de Acidentes em Rodovias Federais',
               style_function=lambda x: {'fillColor': colormap(datatran_uf.loc[int(x['properties']['codarea']),
                                                                           "total_acidentes"]),
                                         'color': 'black','weight':2, 'fillOpacity':0.8},
               tooltip=folium.GeoJsonTooltip(fields=['nome','total_acidentes'], 
                                            aliases=['Estado:','Total de Acidentes:'], 
                                            localize=True)
              ).add_to(m)

# folium.GeoJson(brazil_json,
#                name='Total de Infrações em Rodovias Federais',
#                style_function=lambda x: {'fillColor': colormap(datainfra_uf.loc[int(x['properties']['codarea']),
#                                                                            "total_infracoes"]),
#                                          'color': 'black','weight':2, 'fillOpacity':0.8},
#                tooltip=folium.GeoJsonTooltip(fields=['nome','total_infracoes'], 
#                                             aliases=['Estado:','Total de Infrações:'], 
#                                             localize=True),
#                 show=False
#               ).add_to(m)

# Add um LayerControl
folium.LayerControl().add_to(m)

# Adicinando legenda Color Map
colormap.add_to(m)
# colormap2.add_to(m)

# Salva o mapa
m.save('choropleth.html')