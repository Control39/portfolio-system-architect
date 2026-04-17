import React, { useState, useEffect } from 'react';
import Joyride from 'react-joyride';

const Tutorial = ({ tutorialId, onComplete }) => {
  const [run, setRun] = useState(false);
  const [steps, setSteps] = useState([]);

  useEffect(() => {
    // Загружаем туториал
    fetch(`/tutorials/${tutorialId}.json`)
      .then(res => res.json())
      .then(data => {
        setSteps(data.steps);
        setRun(true);
      });
  }, [tutorialId]);

  const handleJoyrideCallback = (data) => {
    const { status } = data;
    if (status === 'finished' || status === 'skipped') {
      setRun(false);
      if (onComplete) onComplete();
    }
  };

  return (
    <Joyride
      steps={steps}
      run={run}
      continuous={true}
      showProgress={true}
      showSkipButton={true}
      callback={handleJoyrideCallback}
      styles={{
        options: {
          primaryColor: '#007acc',
          backgroundColor: '#2d2d2d',
          textColor: '#fff',
          arrowColor: '#2d2d2d'
        },
        tooltipContainer: {
          textAlign: 'left'
        },
        tooltipTitle: {
          color: '#fff',
          fontSize: 18
        },
        tooltipContent: {
          color: '#a0a0a0'
        },
        buttonNext: {
          backgroundColor: '#007acc',
          color: '#fff'
        },
        buttonBack: {
          color: '#a0a0a0'
        }
      }}
    />
  );
};

export default Tutorial;