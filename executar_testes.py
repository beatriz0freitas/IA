"""
Script para executar todos os testes organizadamente.
"""

import unittest
import sys
from pathlib import Path

# Adiciona raiz ao path
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))


def executar_testes_por_categoria():
    """Executa testes organizados por categoria."""
    
    categorias = [
        ("Testes Unitários", "testes/unitarios"),
        ("Testes de Algoritmos", "testes/algoritmos"),
        ("Testes de Integração", "testes/integracao"),
        ("Testes de Cenários", "testes/cenarios"),
    ]
    
    resultados_totais = {
        "executados": 0,
        "sucessos": 0,
        "falhas": 0,
        "erros": 0
    }
    
    for nome_categoria, diretorio in categorias:
        print(f"\n{'='*80}")
        print(f"{nome_categoria}")
        print(f"{'='*80}\n")
        
        # Descobre testes no diretório
        loader = unittest.TestLoader()
        suite = loader.discover(diretorio, pattern='test_*.py')
        
        # Executa
        runner = unittest.TextTestRunner(verbosity=2)
        resultado = runner.run(suite)
        
        # Atualiza contadores
        resultados_totais["executados"] += resultado.testsRun
        resultados_totais["sucessos"] += resultado.testsRun - len(resultado.failures) - len(resultado.errors)
        resultados_totais["falhas"] += len(resultado.failures)
        resultados_totais["erros"] += len(resultado.errors)
    
    # Resumo final
    print(f"\n{'='*80}")
    print("RESUMO GERAL")
    print(f"{'='*80}")
    print(f"Testes executados: {resultados_totais['executados']}")
    print(f"✓ Sucessos: {resultados_totais['sucessos']}")
    print(f"✗ Falhas: {resultados_totais['falhas']}")
    print(f"⚠ Erros: {resultados_totais['erros']}")
    
    taxa_sucesso = (resultados_totais['sucessos'] / resultados_totais['executados'] * 100
                   if resultados_totais['executados'] > 0 else 0)
    print(f"\nTaxa de sucesso: {taxa_sucesso:.1f}%")
    
    return resultados_totais['falhas'] + resultados_totais['erros'] == 0


if __name__ == '__main__':
    sucesso = executar_testes_por_categoria()
    sys.exit(0 if sucesso else 1)