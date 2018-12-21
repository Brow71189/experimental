# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 18:17:31 2018

@author: Andreas
"""

class ComputationUIPanelDelegate(object):

    def __init__(self, api):
        self.__api = api
        self.panel_id = 'ComputationUI-Panel'
        self.panel_name = 'Computation'
        self.panel_positions = ['left', 'right']
        self.panel_position = 'right'
        self.api = api

    def create_panel_widget(self, ui, document_controller):
        self.ui = ui
        self.document_controller = document_controller
        self.__display_item_changed_event_listener = (
                                 document_controller._document_controller.focused_display_item_changed_event.listen(
                                                                                         self.__display_item_changed))
        self.__computation_updated_event_listener = None

        self.column = ui.create_column_widget()

        return self.column

    def __update_computation_ui(self, computation):
        self.column._widget.remove_all()
        create_panel_widget = getattr(computation, 'create_panel_widget', None)
        if create_panel_widget:
            try:
                widget = create_panel_widget(self.ui, self.document_controller)
            except Exception as e:
                print(str(e))
                import traceback
                traceback.print_exc()
            else:
                self.column.add(widget)

    def __display_item_changed(self, display_item):
        data_item = display_item.data_item if display_item else None
        if data_item:
            if self.__computation_updated_event_listener:
                self.__computation_updated_event_listener.close()
                self.__computation_updated_event_listener = None
            computations = self.document_controller._document_controller.document_model.computations
            found_it = False
            for computation in computations:
                for result in computation.results:
                    if result.specifier.get('uuid') == str(data_item.uuid):
                        found_it = True
                        break
                if found_it:
                    break

            if found_it:
                self.__update_computation_ui(computation)
                self.__computation_updated_event_listener = self.document_controller._document_controller.document_model.computation_updated_event.listen(
                                                                   lambda: self.__update_computation_ui(computation))
            else:
                self.column._widget.remove_all()

    def close(self):
        self.__display_item_changed_event_listener.close()
        self.__display_item_changed_event_listener = None

class ComputationUIExtension(object):
    extension_id = 'nion.extension.computation_ui'

    def __init__(self, api_broker):
        api = api_broker.get_api(version='1', ui_version='1')
        self.__panel_ref = api.create_panel(ComputationUIPanelDelegate(api))

    def close(self):
        self.__panel_ref.close()
        self.__panel_ref = None