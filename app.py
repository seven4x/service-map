import json
import requests
import argparse


# load json from file and convert it to dict
def load_json(file_name):
  with open(file_name) as f:
    return json.load(f)


# revert a dict
def revert_dict(data):
  # foreach a dict
  res = {}
  for key, value in data.items():
    for dep in value['calls']:
      if dep not in res:
        res[dep] = {"called": []}
      if key not in res[dep]['called']:
        res[dep]["called"].append(key)
  return res


Max_Deep = 7


# return service's dependencies path
# result struct is {service: [{}, {}, {service: [{}, {dep2}, ...]}]}
def query_dep_path(service, deps, queried, deep, path):
  if service not in deps or len(deps[service][path]) == 0 or deep > Max_Deep:
    print("query dep:{} pass".format(service))
    return {service: []}
  call = deps[service][path]
  print("query dep:{} from {}".format(service, call))
  resWap = {}
  res = []
  for idx, dep in enumerate(call):
    if dep in queried and deep > 1:
      print("dep:{} is queried".format(dep))
      res.append({dep: []})
      continue
    else:
      queried[dep] = True
    deep = deep + 1
    dep_with_dep = query_dep_path(dep, deps, queried, deep, path)
    deep = deep - 1
    res.append(dep_with_dep)
  resWap[service] = res
  return resWap


def get_args():
  parser = argparse.ArgumentParser()
  parser.add_argument('--service', type=str,
                      help="service you want to query", default='people-peopleserver')
  parser.add_argument('--json_file', type=str,
                      help="please download from "
                           "https://docs.datadoghq.com/api/latest/service-dependencies/#get-one"
                           "-apm-services-dependencies by your own account",
                      default="/Users/lei.zhang/Desktop/services.json")
  parser.add_argument('--route', type=str, help="call or called", default="call")

  args = parser.parse_args()
  return args


if __name__ == '__main__':
  print("Starting")
  args = get_args()
  deps = load_json(args.json_file)
  depeds = revert_dict(deps)
  res = {}
  if args.route == 'called':
    res = query_dep_path(args.service, depeds, {}, 0, 'called')
  else:
    res = query_dep_path(args.service, deps, {}, 0, 'calls')
  print(json.dumps(res, indent=2))
  print("End")
