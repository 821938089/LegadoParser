import CryptoJS from 'crypto-js'
import dayjs from 'dayjs'

let java = {}

java.md5Encode = function (message) {
  return CryptoJS.MD5(message).toString()
}

java.md5Encode16 = function (message) {
  return CryptoJS.MD5(message).toString().substring(8, 24)
}

java.put = function (key, value) {
  pyPut(key, value)
  return value
}

java.get = function (key) {
  return pyGet(key)
}

java.ajax = function (url) {
  return pyAjax(url)
}

java.aesBase64DecodeToString = function (str, key, transformation, iv) {
  let ciphertext = CryptoJS.enc.Base64.parse(str)
  key = CryptoJS.enc.Utf8.parse(key)
  if (iv) {
    iv = CryptoJS.enc.Utf8.parse(iv)
  }
  let algorithm, mode, padding
  ;[algorithm, mode, padding] = transformation.split('/')
  switch (padding) {
    case 'PKCS5Padding':
      padding = CryptoJS.pad.Pkcs7
      break
    case 'NoPadding':
      padding = CryptoJS.pad.NoPadding
      break
    case 'ISO10126Padding':
      padding = CryptoJS.pad.Iso10126
      break

    default:
      break
  }
  let decrypted = CryptoJS.AES.decrypt(
    {
      ciphertext: ciphertext
    },
    key,
    {
      mode: CryptoJS.mode[mode],
      padding: padding,
      iv: iv
    }
  )
  let plaintext = decrypted.toString(CryptoJS.enc.Utf8)
  return plaintext
}

java.timeFormat = function (time) {
  return dayjs(time).format('YYYY/MM/DD HH:mm')
}

java.getZipStringContent = function (url, path) {
  return pyGetZipStringContent(url, path)
}

java.getString = function (rule, isUrl) {
  return pyGetString(rule, isUrl)
}

export { java }
