package main

import (
	"bytes"
	"fmt"
	"net/http"
	"net/http/httputil"
	"net/url"
	"sort"
	"strings"
)

const HostPrefix = "http://127.0.0.1:8080/"

func NewServer(enableLog bool) *Server {
	director := func(req *http.Request) {
		if _, ok := req.Header["User-Agent"]; !ok {
			// explicitly disable User-Agent so it's not set to default value
			req.Header.Set("User-Agent", "")
		}
	}
	return &Server{proxy: &httputil.ReverseProxy{Director: director}, enableLog: enableLog}
}

type Server struct {
	proxy     *httputil.ReverseProxy
	enableLog bool
}

func buildHostPath(u *url.URL) string {
	return "/" + u.Scheme + "://" + u.Host
}

func (s Server) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	targetUrl := r.URL.RequestURI()
	targetUrl = targetUrl[1:]
	target, err := url.Parse(targetUrl)
	if err != nil {
		w.WriteHeader(500)
		return
	}
	r.Host = target.Host
	r.URL = target
	mw := &MWriter{Next: s.proxy.ServeHTTP, EnableLog: s.enableLog}

	if strings.HasSuffix(targetUrl[:strings.LastIndexByte(targetUrl, '/')], "/info/lfs/objects") {
		mw.ReplaceFunc = func(mw *MWriter) {
			for k, v := range mw.cache.header {
				if k == "Content-Length" {
					continue
				}
				mw.writer.Header()[k] = v
			}
			if mw.cache.statusCode != 0 {
				mw.writer.WriteHeader(mw.cache.statusCode)
			}
			content := mw.cache.body.String()
			content = strings.ReplaceAll(content, "\"href\":\"https://", "\"href\":\""+HostPrefix+"https://")
			_, _ = mw.writer.Write([]byte(content))
		}
	}
	mw.ServeHTTP(w, r)
}

type MWriter struct {
	writer  http.ResponseWriter
	request *http.Request
	cache   struct {
		header     http.Header
		body       bytes.Buffer
		statusCode int
	}
	wroteLog bool

	Next        func(http.ResponseWriter, *http.Request)
	ReplaceFunc func(*MWriter)
	EnableLog   bool
}

func (mw *MWriter) Log() {
	if mw.EnableLog && !mw.wroteLog {
		if mw.cache.statusCode == 0 {
			mw.cache.statusCode = http.StatusOK
		}
		fmt.Println(mw.request.Method, mw.request.URL.String(), mw.cache.statusCode)
		header := mw.writer.Header()
		if mw.ReplaceFunc != nil {
			header = mw.cache.header
		}
		var keys []string
		for key := range header {
			keys = append(keys, key)
		}
		sort.Strings(keys)
		for _, key := range keys {
			for _, value := range header[key] {
				fmt.Printf("%s: %s\n", key, value)
			}
		}
		fmt.Println()
		mw.wroteLog = true
	}
}

func (mw *MWriter) Write(data []byte) (int, error) {
	mw.Log()
	if mw.ReplaceFunc == nil {
		return mw.writer.Write(data)
	}
	return mw.cache.body.Write(data)
}

func (mw *MWriter) WriteHeader(statusCode int) {
	for i := range mw.Header()["Location"] {
		location := mw.Header()["Location"][i]
		if locationUrl, _ := url.Parse(location); locationUrl != nil && locationUrl.Scheme != "" {
			location = "/" + location
		} else if location[0] == '/' {
			location = buildHostPath(mw.request.URL) + location
		} else if mw.request.URL.Path == "" { // fix relative path redirect rule
			location = buildHostPath(mw.request.URL) + "/" + location
		}
		mw.Header()["Location"][i] = location
	}
	mw.Log()
	if mw.ReplaceFunc == nil {
		mw.writer.WriteHeader(statusCode)
	}
	mw.cache.statusCode = statusCode
}

func (mw *MWriter) Header() http.Header {
	if mw.ReplaceFunc == nil {
		return mw.writer.Header()
	}
	if mw.cache.header == nil {
		mw.cache.header = mw.writer.Header().Clone()
	}
	return mw.cache.header
}

func (mw *MWriter) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	mw.writer = w
	mw.request = r
	mw.Next(mw, r)
	if mw.ReplaceFunc != nil {
		mw.ReplaceFunc(mw)
	}
}

func main() {
	http.ListenAndServe(":8080", NewServer(true))
}
