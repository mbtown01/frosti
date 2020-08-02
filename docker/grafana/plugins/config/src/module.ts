import { PanelPlugin } from '@grafana/data';
import { ConfigPanel, ConfigPanelOptions } from './ConfigPanel';

export const plugin = new PanelPlugin<ConfigPanelOptions>(
  ConfigPanel
).setPanelOptions(builder => {
  return builder
    .addTextInput({
      path: 'text',
      name: 'Simple text option',
      description: 'Description of panel option',
      defaultValue: 'Default value of text input option',
    })
    .addBooleanSwitch({
      path: 'showSeriesCount',
      name: 'Show series counter',
      defaultValue: false,
    });
});
