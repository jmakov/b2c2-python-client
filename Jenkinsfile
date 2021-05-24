pipeline {
    agent any

    stages {
        stage("MyPy"){
            steps{
                catchError(buildResult: 'SUCCESS', message: 'MyPy found issues', stageResult: 'UNSTABLE') {
                    sh (label: "Running MyPy",
                        script: """mkdir -p reports/mypy
                                   mkdir -p logs
                                   mypy src --html-report reports/mypy/mypy_html > logs/mypy.log"""
                        )
                }
            }
        }
        stage('Test') {
            steps {
                script {
                    def envs = sh(returnStdout: true, script: "tox -l").trim().split('\n')
                    def cmds = envs.collectEntries({ tox_env ->
                        [tox_env, {
                        sh "tox --parallel--safe-build -vve $tox_env"
                        }]
                    })
                    parallel(cmds)
                }
            }
        }
    }
}