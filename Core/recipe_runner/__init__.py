from Core.actions import QuickShutdownAllDeviceElementsAction
from coregraphene.recipe import RecipeRunner


class AppRecipeRunner(RecipeRunner):
    def _on_not_achieving_recipe_step_action(self):
        shutdown_action = QuickShutdownAllDeviceElementsAction()
        shutdown_action.set_functions(system=self._system)
        shutdown_action.action()
