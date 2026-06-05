# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Project Build / Deployment Quick Reference

This project has two deployable parts:

- Frontend React app: built into the root `build/` folder.
- Backend Flask/Lambda app: packaged into `backend/deployment.zip`.

### Frontend production build

From the project root:

```powershell
cd D:\project\JehyeonAssetManagement\jay-asset
npm run build
```

This creates:

```text
build/
```

Upload this folder to the chosen frontend hosting target, such as S3/CloudFront or AWS Amplify.

### Backend Lambda package build

The backend Lambda package should be built with Docker so packages like `numpy` and `pandas`
are installed for the Linux runtime used by AWS Lambda.

From the project root:

```powershell
cd D:\project\JehyeonAssetManagement\jay-asset

docker ps

docker run --rm `
  -v "${PWD}/backend:/var/task" `
  public.ecr.aws/sam/build-python3.11:latest `
  /bin/sh -c "rm -rf /var/task/lambda_build /var/task/deployment.zip && mkdir -p /var/task/lambda_build && pip install -r /var/task/requirements.txt -t /var/task/lambda_build && cp /var/task/*.py /var/task/lambda_build/ && cp -r /var/task/strategies /var/task/cache /var/task/market /var/task/performance /var/task/lambda_build/ && cd /var/task/lambda_build && zip -r /var/task/deployment.zip ."

Get-Item .\backend\deployment.zip
```

This creates:

```text
backend/deployment.zip
```

Upload this zip to the AWS Lambda function that uses:

```text
Runtime: Python 3.11
Handler: lambda_handler.handler
```

For more backend-specific deployment details, see `backend/README.md`.

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)
