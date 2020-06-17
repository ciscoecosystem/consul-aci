
// function for showing show name if in case of bigger name
export const showShortName = (dataString, strLen) => {
  if (typeof (dataString) === "string") {
    if (dataString.length > strLen) {
      return dataString.substr(0, strLen) + ".."
    }
    return dataString
  }
  else
    return dataString

}

// function for showing value in K, M and T
export const nFormatter = (num) => {
  if (typeof (num) !== "number") {
    return num
  }
  if (num >= 1000000000) {
    return (num / 1000000000).toFixed(1).replace(/\.0$/, '') + 'B';
  }
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
  }
  return num;
}