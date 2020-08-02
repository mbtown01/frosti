import React from 'react';
import { useState, useEffect } from "react";
import { PanelProps, ColorScheme } from '@grafana/data';
import { css, cx } from 'emotion';
import { stylesFactory } from "@grafana/ui";
import { Button, Label, Input } from "@grafana/ui";
// import { stylesFactory, useTheme } from '@grafana/ui';

// URL for the thermostat API is at the same host but on a different port
var URL_BASE = `http://${window.location.hostname}:5000`;
// Holds all the changed config values
var CHANGED_CONFIG_MAP = new Map<string, string>();


// ###########################################################################
// A single configuration entry component that takes the user input and
// stores it in the config data to be posted at the user's request
interface ConfigEntryProps {
  name: string;
  value: string;
  width: number;
};

const ConfigEntry: React.FunctionComponent<ConfigEntryProps> = (props) => {
  const [inputValue, setInputValue] = useState<string>(props.value);
  const styles = getStyles(props.width);

  const labelStyle = css({
    width: '100px',
  });

  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value);
    console.log('setting global value', event.target.name, event.target.value)
    CHANGED_CONFIG_MAP.set(event.target.name, event.target.value);
  }

  return (
    <div css={styles.divStyle}>
      <Label key={`${props.name}.label`} css={labelStyle}>{props.name}</Label>
      <Input key={`${props.name}.input`} type='text' name={props.name} value={inputValue} onChange={handleChange}></Input>
    </div>);
};

// ###########################################################################
// State data for the ConfigPanel
const useConfigData = () => {
  const [configData, setConfigData] = useState(new Map<string, string>());

  const getConfigData = async () => {
    let response = await fetch(`${URL_BASE}/api/config`, { method: "GET" });
    let jsonData = await response.json();
    let updatedConfigData = new Map<string, string>();
    for (var key in jsonData) {
      updatedConfigData.set(key, jsonData[key]);
    }

    setConfigData(updatedConfigData);
  };

  return { configData, setConfigData, getConfigData };
};


// ###########################################################################
// ConfigPanel 
export interface ConfigPanelOptions {
  text: string;
  showSeriesCount: boolean;
}

interface ConfigPanelProps extends PanelProps<ConfigPanelOptions> { }

function GetConfigData() {
  const { getConfigData } = useConfigData();

  useEffect(() => {
    console.log('GetConfigData in effect');
    getConfigData()
  }, []);

  return <div></div>;
}

export const ConfigPanel: React.FunctionComponent<ConfigPanelProps> = ({ options, data, width, height }) => {
  const styles = getStyles(width);

  const {
    configData,
    getConfigData
  } = useConfigData();

  let configEntryList: Array<JSX.Element> = [];
  let sortedMap = new Map([...configData.entries()].sort())
  sortedMap.forEach((value: string, key: string) => {
    configEntryList.push(<ConfigEntry key={key} name={key} value={value} width={width} />);
  });

  const OnUpdateButtonClicked = async () => {
    getConfigData();
  };

  const OnSubmitButtonClicked = async () => {
    const rawResponse = await fetch(`${URL_BASE}/api/config`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(Object.fromEntries(CHANGED_CONFIG_MAP))
    });

    await rawResponse.json();
    CHANGED_CONFIG_MAP.clear()
  };

  return (
    <div
      className={cx(
        styles.wrapper,
        css({ width: width, height: height })
      )}
    >
      <form>
        {configEntryList}
      </form>
      <Button onClick={OnUpdateButtonClicked}>Update</Button>
      <Button onClick={OnSubmitButtonClicked}>Submit</Button>
      <GetConfigData />
    </div >
  );
};

// Random styles put here so they don't make the code even harde to read...
const getStyles = stylesFactory((width: number) => {
  return {
    wrapper: css({
      position: 'relative',
    }),
    svg: css({
      position: 'absolute',
      top: 0,
      left: 0,
    }),
    textBox: css({
      position: 'absolute',
      bottom: 0,
      left: 0,
      padding: 10,
    }),
    divStyle: css({
      width: `${width}px`,
      marginTop: '5px',
      marginBottom: '5px',
      marginLeft: '0px',
      marginRight: '0px',
      display: 'flex',
      flexGrow: 1,
      flexDirection: 'row',
    }),
  };
});
