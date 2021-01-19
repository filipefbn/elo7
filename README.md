![](https://images.elo7.com.br/assets/v3/desktop/svg/logo-elo7.svg)

### Repositório referente ao teste prático para o processo seletivo Elo7 para a vaga de Data Scientist (Information Retrieval)
#

## Organização

As classes referentes à implementação do `text-based search engine` se encontram no arquivo `search.py`. Um exemplo de uso do motor de busca pode ser visto no notebook `Ranking Evaluation.ipynb`, bem como uma breve avaliação de qualidade de ranking em conjunto com análise posterior dos resultados.


## Considerações
* O modelo de ranking implementado foi o Okapi-BM25. Essa escolha se deu devido à menção do uso do modelo durante a etapa anterior de entrevista e também pelo fato de ser um modelo amplamente utilizado na área. Um link de referência para o modelo pode ser encontrado na classe `BM25Ranker` em `search.py`.

* Foi abstraída a noção de armazenamento e acesso eficiente dos documentos. Para os propósitos desse teste, restringimos a atenção apenas à recuperação/ranqueamento do id dos produtos. Assim, o índice construído "não se preocupa" em como as informações adicionais dos documentos são acessadas.

#

Finalmente, me coloco à disposição para quaisquer esclarecimentos referentes às escolhas de implementação e ao código em si.
