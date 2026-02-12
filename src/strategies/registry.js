import GenericConfigPanel, { buildGenericParameters } from './panels/GenericConfigPanel';
import PAAConfigPanel, { buildPAAParameters } from './panels/PAAConfigPanel';
import VAAConfigPanel, { buildVAAParameters } from './panels/VAAConfigPanel';

export const getStrategyConfigPanel = (strategyId) => {
  if (strategyId === 'paa') return PAAConfigPanel;
  if (strategyId === 'vaa') return VAAConfigPanel;
  return GenericConfigPanel;
};

export const buildStrategyParameters = (strategyId, paramDefs, paramValues) => {
  if (strategyId === 'paa') return buildPAAParameters(paramValues);
  if (strategyId === 'vaa') return buildVAAParameters(paramValues);
  return buildGenericParameters(paramDefs, paramValues);
};

