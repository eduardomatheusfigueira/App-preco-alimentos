# -*- coding: utf-8 -*-
"""
Cliente HTTP para a API do Menor Preço (Nota Paraná).
Inclui pausas automáticas e retry para respeitar o servidor.
"""

import time
import random
import requests
from config import (
    API_PRODUTOS,
    API_GEOCODING,
    RAIO_BUSCA_KM,
    DELAY_MIN,
    DELAY_MAX,
)


class MenorPrecoAPI:
    """Cliente para acessar a API do portal Menor Preço."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            "Referer": "https://menorpreco.notaparana.pr.gov.br/",
        })
        self._ultima_requisicao = 0

    def _aguardar(self):
        """Pausa aleatória entre requisições para não sobrecarregar o servidor."""
        agora = time.time()
        tempo_desde_ultima = agora - self._ultima_requisicao
        delay = random.uniform(DELAY_MIN, DELAY_MAX)

        if tempo_desde_ultima < delay:
            espera = delay - tempo_desde_ultima
            print(f"  ⏳ Aguardando {espera:.1f}s...")
            time.sleep(espera)

        self._ultima_requisicao = time.time()

    def _fazer_requisicao(self, url, params=None, tentativas=3):
        """Faz requisição HTTP com retry e backoff exponencial."""
        for tentativa in range(tentativas):
            try:
                self._aguardar()
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()

            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:  # Too Many Requests
                    espera = (2 ** tentativa) * 10
                    print(f"  ⚠️  Rate limit! Aguardando {espera}s...")
                    time.sleep(espera)
                elif response.status_code >= 500:
                    espera = (2 ** tentativa) * 5
                    print(f"  ⚠️  Erro do servidor ({response.status_code}). Tentativa {tentativa + 1}/{tentativas}...")
                    time.sleep(espera)
                else:
                    print(f"  ❌ Erro HTTP {response.status_code}: {e}")
                    return None

            except requests.exceptions.ConnectionError:
                espera = (2 ** tentativa) * 5
                print(f"  ⚠️  Erro de conexão. Tentativa {tentativa + 1}/{tentativas}...")
                time.sleep(espera)

            except requests.exceptions.Timeout:
                espera = (2 ** tentativa) * 3
                print(f"  ⚠️  Timeout. Tentativa {tentativa + 1}/{tentativas}...")
                time.sleep(espera)

            except Exception as e:
                print(f"  ❌ Erro inesperado: {e}")
                return None

        print(f"  ❌ Falha após {tentativas} tentativas.")
        return None

    def buscar_produtos(self, termo, geohash, raio=None):
        """
        Busca produtos na API do Menor Preço.

        Args:
            termo: Termo de busca (ex: "Arroz tipo 1")
            geohash: Geohash da localização (ex: "6gkzq99z5j5f")
            raio: Raio de busca em km (padrão da config)

        Returns:
            Lista de produtos ou lista vazia em caso de erro
        """
        if raio is None:
            raio = RAIO_BUSCA_KM

        params = {
            "local": geohash,
            "termo": termo,
            "raio": raio,
        }

        resultado = self._fazer_requisicao(API_PRODUTOS, params)

        if resultado and "produtos" in resultado:
            return resultado["produtos"]

        return []

    def buscar_geohash_cidade(self, cidade):
        """
        Converte nome da cidade em geohash via API do Menor Preço.

        Args:
            cidade: Nome da cidade (ex: "Curitiba")

        Returns:
            Geohash string ou None em caso de erro
        """
        params = {"regiao": cidade}
        resultado = self._fazer_requisicao(API_GEOCODING, params)

        if resultado and len(resultado) > 0:
            geohash = resultado[0].get("geohash")
            if geohash:
                print(f"  📍 {cidade} → geohash: {geohash}")
                return geohash

        print(f"  ❌ Não foi possível obter geohash para '{cidade}'")
        return None
