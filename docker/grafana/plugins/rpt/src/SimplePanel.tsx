import { useState } from 'react';
import React from 'react';

import { PanelProps } from '@grafana/data';
import { SimpleOptions } from 'types';
import { css, cx } from 'emotion';
import { stylesFactory } from '@grafana/ui';
import { Button } from '@grafana/ui';
//import { stylesFactory, useTheme } from '@grafana/ui';

interface Props extends PanelProps<SimpleOptions> {}

const URL_BASE: string = 'http://localhost:5000';

const useThermostatState = () => {
  const [mode, setMode] = useState('NONE');
  const [state, setState] = useState('NONE');
  const [comfortMin, setComfortMin] = useState('99');
  const [comfortMax, setComfortMax] = useState('49');

  const udpateThermostatState = async () => {
    let response = await fetch(`${URL_BASE}/api/status`, { method: 'GET' });
    let jsonData = await response.json();
    setState(jsonData.state);
    setMode(jsonData.mode);
    setComfortMin(jsonData.comfortMin);
    setComfortMax(jsonData.comfortMax);
  };

  return { mode, state, comfortMin, comfortMax, udpateThermostatState };
};

export const SimplePanel: React.FC<Props> = ({ options, data, width, height }) => {
  //const theme = useTheme();
  const styles = getStyles();

  // if ( data.series.length > 0 ) {
  //   length = data.series[0].length;
  //   if ( length > 0 )
  //     console.debug(data.series[0].fields[1].values.get(length-1));
  // }

  const { mode, state, comfortMin, comfortMax, udpateThermostatState } = useThermostatState();

  if ('NONE' == mode) {
    console.debug('reloading based on mode');
    udpateThermostatState();
  }

  const OnUpdateButtonClicked = async () => {
    udpateThermostatState();
  };

  const onUpButtonClicked = async () => {
    await fetch(`${URL_BASE}/api/action/raiseComfort`, { method: 'POST' });
    udpateThermostatState();
  };

  const onDownButtonClicked = async () => {
    await fetch(`${URL_BASE}/api/action/lowerComfort`, { method: 'POST' });
    udpateThermostatState();
  };

  const onModeButtonClicked = async () => {
    await fetch(`${URL_BASE}/api/action/nextMode`, { method: 'POST' });
    udpateThermostatState();
  };

  const buttonClass = cx(
    styles.wrapper,
    css`
      width: ${width / 2}px;
      text-align: center;
      margin-top: 5px;
      margin-bottom: 5px;
      margin-left: 0px;
      margin-right: 0px;
      flex-grow: 1;
    `
  );

  let stateColor: string = '';
  if (state == 'COOLING') stateColor = '#0000FF';
  else if (state == 'HEATING') stateColor = '#FF0000';
  else if (state == 'FAN') stateColor = '#00FF00';

  const stateElementClass =
    stateColor != ''
      ? cx(
          styles.wrapper,
          css`
            background-color: ${stateColor};
          `
        )
      : cx(styles.wrapper, css``);

  return (
    <div
      className={cx(
        styles.wrapper,
        css`
          width: ${width}px;
          display: flex;
          flex-direction: row;
          align-items: center;
        `
      )}
    >
      <div
        className={cx(
          styles.wrapper,
          css`
            height: ${height}px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            flex-grow: 1;
          `
        )}
      >
        <Button className={buttonClass} onClick={onUpButtonClicked}>
          Up
        </Button>
        <Button className={buttonClass} onClick={onDownButtonClicked}>
          Down
        </Button>
        <Button className={buttonClass} onClick={onModeButtonClicked}>
          Mode
        </Button>
        <Button className={buttonClass} onClick={OnUpdateButtonClicked}>
          Update
        </Button>
      </div>
      <div
        className={cx(
          styles.wrapper,
          css`
            height: ${height}px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            flex-grow: 1;
          `
        )}
      >
        <span>Mode: {mode}</span>
        <span className={stateElementClass}>State: {state}</span>
        <span>
          Targets {comfortMin} / {comfortMax}
        </span>
      </div>
    </div>
  );
};

const getStyles = stylesFactory(() => {
  return {
    wrapper: css`
      position: relative;
    `,
  };
});
