import time
import solution

class Solver:

    def __init__(self,
                 max_time_sec=10):
        self.max_time_sec = max_time_sec
        self._last_run_start = 0 
        self._last_run_end = 0
        self.verbose = 1

    def _prepare(self):
        #Initialiser tous les attributs pour l'éxécution
        self._last_run_sec = 0
        #Démarrer le chrono
        self._last_run_start = time.time()

    def _continue(self):
        elapsed_time = time.time() - self._last_run_start
        if elapsed_time <= self.max_time_sec:
            return True
        return False
    
    def _terminate(self):
        #arreter le chorno et calculer le temps utilisé
        self._last_run_end = time.time()
        self._last_run_sec = self._last_run_end-self._last_run_start

    def solve(self, prob=None):
        # Préparer exécution
        self._prepare()
        # Boucle d'exécution
        while(self._continue()):
            # TODO Coder la boucle d'exécution ici à la place de pass            
            pass

        # Finaliser exécution
        self._terminate()

        # Retourner une solution
        # TODO Le code ci-dessous est un code temporaire
        return solution.Solution()