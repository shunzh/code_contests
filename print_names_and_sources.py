# Copyright 2022 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""A simple tool to iterate through the dataset, printing the name and source.

Example usage:

  print_names_and_sources /path/to/dataset/code_contests_train*
"""

import io
import json
import os
import sys

import riegeli

import contest_problem_pb2

from google.protobuf.json_format import MessageToJson


def _all_problems(filenames):
  """Iterates through all ContestProblems in filenames."""
  for filename in filenames:
    reader = riegeli.RecordReader(io.FileIO(filename, mode='rb'),)
    for problem in reader.read_messages(contest_problem_pb2.ContestProblem):
      yield problem


def _print_names_and_sources(filenames):
    """Prints the names and sources of all ContestProblems in filenames."""
    for problem in _all_problems(filenames):
        print(
            contest_problem_pb2.ContestProblem.Source.Name(problem.source),
            problem.name)


# mapping between saved file name and program attribute
mapping = [("public_test_cases.json", 'publicTests'),
           ("private_test_cases.json", 'privateTests'),
           ("generated_test_cases.json", 'generatedTests'),
           ("solutions.json", 'solutions'),
           ("question.txt", 'description')]

def _process_input_output(test_cases):
    """
    this dataset contains test cases as [{input, output}, {input, output}, ...]
    need it to be {'inputs': [input, input, ...], 'outputs': [output, output...]}
    """
    inputs = []
    outputs = []
    for datum in test_cases:
        inputs.append(datum['input'])
        outputs.append(datum['output'])
    return {'inputs': inputs, 'outputs': outputs}

def _convert_to_apps_format(filenames, save_dir):
  os.makedirs(save_dir, exist_ok=True)

  for problem in _all_problems(filenames):
    prob_path = os.path.join(save_dir, str(problem.name)) # use problem name as path name
    os.makedirs(prob_path, exist_ok=True)

    problem = json.loads(MessageToJson(problem))

    for filename, attribute in mapping:
      if attribute in problem.keys():
        print(f'saving {attribute}')

        file_path = os.path.join(prob_path, filename)

        if attribute in ['publicTests', 'privateTests', 'generatedTests']:
          problem[attribute] = _process_input_output(problem[attribute])

        with open(file_path, 'w') as f:
          json.dump(problem[attribute], f)
      else:
        print(f"problem {problem['source']} does not have attribute {attribute}")


if __name__ == '__main__':
  #_print_names_and_sources(sys.argv[1:])
  _convert_to_apps_format(sys.argv[1:], save_dir='/u/shunzhang/code_contests/CodeContests')
