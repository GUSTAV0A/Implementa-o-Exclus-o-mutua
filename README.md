# Implementacao Exclusao mutua

Script Powershell para executar varios processos simultanemanete:

- Atualizar valor de N e o caminho do arquivo

for ($i = 1; $i -le N; $i++) {
    Start-Process python -ArgumentList "path", $i
}