# Desafio técnico da Meliuz

## Como executar este projeto

Para executar, rode o seguinte comando:

```
docker compose up -d --build
```

Para parar a execução

```
docker compose down
```

## Rotas

- Em `http://localhost:8000/docs` será possível visualizar o swagger com as rotas
  disponíveis.
- A única rota disponível é `http://localhost:8000/api/v1/recommendations?user_id=<number>`
  - deve-se informar o `user_id`. O `user_id` não interfere no resultado, mas
    foi exigido para o desafio
  - esta rota retornar os top 5 produtos conforme os pesos do arquivo `.env`

## Análise dos dados

Primeiro vamos analisar os 5 produtos mais vendidos. Uma primeira solução
seria simplesmente retornar os produtos mais vendidos

|     | product_id | product_title                | min_product_price | max_product_price | avg_product_price | total_sales |
| --: | ---------: | :--------------------------- | ----------------: | ----------------: | ----------------: | ----------: |
|   0 |         36 | Home Theater Sony            |             11.13 |             18.76 |           15.1335 |         312 |
|   1 |         47 | HD Externo Seagate           |            561.32 |            981.27 |            754.49 |         290 |
|   2 |         29 | Caixa de Som Bluetooth Bose  |            566.65 |           1007.42 |           805.839 |         283 |
|   3 |         21 | Ar Condicionado Split LG     |            666.45 |           1201.25 |            939.11 |         262 |
|   4 |         12 | Impressora Multifuncional HP |            311.12 |            555.13 |           421.817 |         260 |

Analisando os produtos mais vendidos podemos ver que o preço médio do segundo
ao quinto são muito altos. Apenas o primeiro produto tem um preço mais baixo.
Isso levanta um questionamento: será se o número de vendas aumentará ao retornar apenas os 5 mais vendidos, mesmo que 4 desses produtos estejam na casa de centenas de reais?

Para isso, vamos analisar também os 10 produtos com menor preço médio

|     | product_id | product_title                      | min_product_price | max_product_price | avg_product_price | total_sales |
| --: | ---------: | :--------------------------------- | ----------------: | ----------------: | ----------------: | ----------: |
|   0 |         45 | Placa de Vídeo NVIDIA GeForce      |              8.35 |             14.98 |           11.5412 |         141 |
|   1 |         36 | Home Theater Sony                  |             11.13 |             18.76 |           15.1335 |         312 |
|   2 |         25 | Panela de Pressão Elétrica Mondial |             25.15 |             45.26 |           35.1722 |         206 |
|   3 |         39 | Chaleira Elétrica Oster            |                35 |             56.74 |           44.2442 |         144 |
|   4 |         23 | Ventilador de Mesa Arno            |             52.16 |             84.81 |           66.3567 |         155 |
|   5 |         31 | Smartwatch Xiaomi                  |              69.7 |             120.2 |           108.722 |         119 |
|   6 |         49 | Processador Intel Core i7          |             91.73 |            155.73 |           120.748 |         152 |
|   7 |         42 | Termômetro Digital G-Tech          |             88.63 |            151.41 |           124.314 |         227 |
|   8 |         27 | Drone DJI Phantom                  |             113.5 |            190.69 |           155.145 |         216 |
|   9 |         13 | Monitor Gamer AOC                  |            185.53 |            331.04 |           259.575 |         198 |

Os top 10 produtos com menor preço médio parecem bem interessantes. Por exemplo,
a placa de vídeo está a um preço muito atraente. Os 5 primeiros possuem preços
abaixo dos cem reais, o que talvez seja um atrativo para os novos consumidores
realizarem a compra sem ter que gastar muito. Mas levanta um novo questionamento:
Será se apenas exibir os produtos com preço menor médio aumentará o número de ganhos?

## Solução

### Da heurística

Com as análises acima, tive a ideia de gerar um score em que se baseia no preço
e no total de vendas. A fórmula dessa heurística se dá por:
$$ {1 \over price} \times totalSales $$

Essa fórmula se inspira no tf-idf. O total de vendas seria equivalente ao tf,
pois seriam os produtos mais frequentemente vendidos. Enquanto o o inverso do
valor preço teria o mesmo papel do idf, mas no caso com ênfase nos produtos
de menor preço. Como queremos aumentar as vendas, precisamos levar esses dois
valores em conta.

Outro fator a se prestar atenção é a data de venda.

|     | sale_date  | product_id | product_title                 | product_price | product_image_url                  | store_name | store_id | sales_per_day |
| --: | :--------- | ---------: | :---------------------------- | ------------: | :--------------------------------- | :--------- | -------: | ------------: |
|   0 | 2024-05-15 |          1 | Smartphone Samsung Galaxy S21 |        555.87 | https://www.lorempixel.com/486/36  | Amazon     |        1 |             5 |
|   1 | 2024-05-05 |          1 | Smartphone Samsung Galaxy S21 |        529.55 | https://www.lorempixel.com/868/364 | Amazon     |        1 |             8 |

Analisando a venda do produto de id 1 na Amazon, podemos ver que a última data
de venda foi no dia 15 de maio, possivelmente este é o preço mais atualizado do
produto. Portanto irei considerar o último valor de um produto para dada loja.
Neste caso, para o produto de id na Amazon seria o que foi vendido em 15 de maio.

Se pegarmos as últimas vendas do produto 1 de cada loja, vamos obter a seguinte
tabela:

|     | store_id | store_name       | product_id | product_title                 | product_price |
| --: | -------: | :--------------- | ---------: | :---------------------------- | ------------: |
|   0 |        1 | Amazon           |          1 | Smartphone Samsung Galaxy S21 |        555.87 |
|   1 |       12 | Livraria Cultura |          1 | Smartphone Samsung Galaxy S21 |        458.99 |
|   2 |       17 | Ricardo Eletro   |          1 | Smartphone Samsung Galaxy S21 |        595.72 |
|   3 |        9 | Fnac             |          1 | Smartphone Samsung Galaxy S21 |        552.08 |
|   4 |        3 | C&A              |          1 | Smartphone Samsung Galaxy S21 |        487.37 |

É importante retornar o produto de menor valor dessa tabela na hora de computar o score.
Portanto, na hora de computar o score de cada produto, estaríamos considerando
o produto vendido pela livraria cultura.

Computando nosso score, obtemos os seguintes produtos:
| | index | store_id | store_name | product_id | product_title | product_price | total_sales | score |
|---:|--------:|-----------:|:-------------|-------------:|:-----------------------------------|----------------:|--------------:|---------:|
| 0 | 35 | 1 | Amazon | 36 | Home Theater Sony | 11.34 | 312 | 27.5132 |
| 1 | 44 | 7 | Extra | 45 | Placa de Vídeo NVIDIA GeForce | 8.35 | 141 | 16.8862 |
| 2 | 24 | 5 | Casas Bahia | 25 | Panela de Pressão Elétrica Mondial | 26.98 | 206 | 7.63529 |
| 3 | 38 | 16 | Ponto Frio | 39 | Chaleira Elétrica Oster | 39.09 | 144 | 3.68381 |
| 4 | 22 | 15 | Netshoes | 23 | Ventilador de Mesa Arno | 52.16 | 155 | 2.97163 |

Parece promissor, entretanto, seria interessante aplicar um normalização no score.
A normalização escolhida, tanto para o preço quanto para a quantidade de vendas
é a divisão pelo valor máximo, como na fórmula do preço é o inverso, o inverso
do preço será $1 - normalizedPrice$. Com os valores normalizados, podemos
atribuir pesos para para preço normalizado e para o inverso do preço.

Com isso, se tivermos o peso das vendas como 0 e peso dos preços como 1,
teremos os top 5 produtos mais baratos. Se for o contrário, será os top 5
mais vendidos.

$$ score = weightSales \times normalizedSales + weightPrice \times inverseNormalizedPrice$$

Para este desafio, ambos os pesos estarão como 0.5 por motivos práticos. Como resultado, vamos obter os seguintes produtos:

|     | store_name   | product_title                      |    score |
| --: | :----------- | :--------------------------------- | -------: |
|   0 | Amazon       | Home Theater Sony                  | 0.997856 |
|   1 | Casas Bahia  | Panela de Pressão Elétrica Mondial | 0.765809 |
|   2 | Lojas Renner | Termômetro Digital G-Tech          | 0.765355 |
|   3 | Extra        | Drone DJI Phantom                  | 0.724606 |
|   4 | Centauro     | Máquina de Lavar Roupas Brastemp   | 0.696044 |

## Melhorias

### Cache

Acredito que a tabela de produtos mais vendidos seria atualizada mensalmente.
Então seria necessário abrir a tabela a cada requisição. Seria mais
eficiente os top 5 mais recomendados em um cache como o Redis.

### Rotina para computar os top 5

Ainda na premissa de atualização mensal, talvez fosse interessante ter uma
rotina que fizesse o computo dos top 5. Dado que a quantidade de produtos
pode aumentar, seria interessante separar essa responsabilidade da API.
Os top5 produtos recomendados poderiam ser salvos em um cache, ou até
mesmo em um banco relacional. Assim a API teria apenas a responsabilidade
de pegar os top 5 e não computá-los

### Melhorar os pesos

Seria possível melhorar os pesos. Isso poderia ser feito usando aprendizado
de máquina ou ajustando manualmente. Idealmente realizar um teste A/B para
checar se realmente houve ganho.

## Escolhas

### Framework

Escolhi o fastapi como framework por conta de sua simplicidade e eficiência.
Possui uma curva de aprendizado curta, é mais produtivo e facilita a produção
de documentação das rotas.

### Framework de teste

Escolhi o Pytest por ser o framework que estou mais familiarizado. Junto dele
também usei o módulo de cobertura de testes.

### Poetry

Como costumava a fazer a APIs em node, usar o poetry foi uma escolha natural
para gerir as dependências do projeto, lembrando npm.
